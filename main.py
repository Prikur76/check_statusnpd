#!/usr/bin/python

from __future__ import print_function

import time
import pytz
import requests
import pandas as pd

from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app_logger import get_logger
from settings import GOOGLE_SHEETS_PARAMS
from settings import ELEMENT_PARAMS
from settings import ELEMENT_URLS
from settings import STATUSNPD_ENDPOINT_URL
from settings import SERVICE_ACCOUNT_FILE


logger = get_logger(__name__)


def create_sheets_api_client() -> build:
    """Creates a Sheets API client instance."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=creds)


def batch_clear_values(
        spreadsheet_id: str,
        range_names: list[str]) -> dict[str, list[str]]:
    """Clear a single or multiple ranges in a spreadsheet.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        range_names (list[str]): A list of range names to clear.

    Returns:
        dict[str, list[str]]: A dictionary with the cleared range names as keys
            and empty lists as values.
    """
    service = create_sheets_api_client()
    sheet = service.spreadsheets().values()
    request = sheet.batchClear(
        spreadsheetId=spreadsheet_id,
        body={"ranges": range_names}
    )
    response: dict = request.execute()
    if response:
        return response
    raise HttpError()


def batch_update_values(
    spreadsheet_id: str, range_name: str, values: list[list[str]]
) -> dict[str, str]:
    """Batch update values in a spreadsheet.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        range_name (str): The range of cells to update.
        values (list[list[str]]): The values to update.

    Returns:
        dict[str, str]: The response from the Google Sheets API.
    """
    service = create_sheets_api_client()
    sheet = service.spreadsheets().values()
    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [{"range": range_name, "values": values}]
    }
    request = sheet.batchUpdate(spreadsheetId=spreadsheet_id, body=body)
    response = request.execute()
    return {range_name: response["responses"][0]["updatedRange"]}


def check_self_employment_status(inn: str) -> tuple[bool, str | None, str]:
    """Check the self-employment status of a driver.

    Args:
        inn (str): The driver's INN.

    Returns:
        tuple[bool, str | None]:
            A tuple containing a boolean indicating the self-employment status
            and a message. If the driver is self-employed, the message is
            'СМЗ'. If the driver is not self-employed, the message is
            'не СМЗ'. If there's an error, the message is the error message.
    """
    request_date = datetime.now(pytz.timezone('Europe/Moscow'))\
        .strftime('%Y-%m-%d')
    response = requests.post(
        url=STATUSNPD_ENDPOINT_URL,
        json={"inn": inn, "requestDate": request_date},
        timeout=120
    )
    result = response.json()
    is_self_employed = False
    message = "не СМЗ"
    if response.status_code != 200:

        message = result.get("message")
        if "Указан некорректный ИНН" in message:
            message = "Некорректный ИНН"

        attempt = 0
        if 'taxpayer.status.service.limited.error'\
                in result.get("code") and attempt < 3:
            time.sleep(40)
            check_self_employment_status(inn)
            attempt += 1

    if result.get("status"):
        is_self_employed = True
        message = "СМЗ"

    time.sleep(31)

    return is_self_employed, message, request_date


def validate_snils(snils: str) -> tuple[str, bool, str]:
    """Validate a SNILS (Russian Social Insurance Number)."""
    snils = snils.replace("-", "").replace(" ", "")
    is_valid = False
    message = ""
    formatted_snils = ""

    if not snils:
        message = "SNILS cannot be empty"
        return formatted_snils, is_valid, message

    if not snils.isdigit():
        message = "SNILS can only contain digits"
        return formatted_snils, is_valid, message

    if len(snils) != 11:
        message = "SNILS must contain 11 digits"
        return formatted_snils, is_valid, message

    for i in range(len(snils) - 2):
        if snils[i] == snils[i + 1] == snils[i + 2]:
            message = "SNILS cannot contain three repeating digits"
            return formatted_snils, is_valid, message

    sum_products = sum(
        int(digit) * (9 - i) for i, digit in enumerate(snils[:-2])
    )

    if sum_products < 100:
        control_number = sum_products
    elif sum_products == 100 or sum_products == 101:
        control_number = "00"
    else:
        control_number = sum_products % 101

    if str(control_number) == snils[-2:]:
        is_valid = True

    message = "SNILS is not valid"
    formatted_snils = f"{snils[:3]}-{snils[3:6]}-{snils[6:9]} {snils[9:]}"

    return formatted_snils, is_valid, message


def validate_inn_12(inn: str) -> bool:
    """
    Validate an INN (Russian Individual Taxpayer Number) according to
    the rules specified in Federal Law №325-FZ of 2016
    https://keysystems.ru/files/fo/arm_budjet/show_docum/BKS/onlinehelphtm/ro_kr_algor_klyuch_inn.htm
    """
    inn = str(inn)
    is_valid = False
    message = ""

    if not inn:
        message = "ИНН пуст"
        return is_valid, message

    if not inn.isdigit():
        message = "ИНН может состоять только из цифр"
        return is_valid, message

    if len(inn) != 12:
        message = "ИНН физлица должен состоять из 12 цифр"
        return is_valid, message

    if len(inn) == 12:
        coefficients_1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8, 0]
        first_control_num = sum(
            c * int(d) for c, d in zip(coefficients_1, inn[:11])
        ) % 11
        if first_control_num > 9:
            first_control_num = first_control_num % 10
        check_first_control_num = bool(first_control_num == int(inn[10:11]))

        coefficients_2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8, 0]
        second_control_num = sum(
            c * int(d) for c, d in zip(coefficients_2, inn[:11])
        ) % 11
        if second_control_num > 9:
            second_control_num = second_control_num % 10
        check_second_control_num = bool(second_control_num == int(inn[11:12]))

        if check_first_control_num and check_second_control_num:
            is_valid = True
            return is_valid, message
        message = "Неправильное контрольное число"

    return is_valid, message


def fetch_active_drivers_with_inn() -> pd.DataFrame:
    """Retrieve a list of active drivers from 1C:Element"""
    url = "".join(tuple(ELEMENT_URLS.values()))
    auth = tuple(ELEMENT_PARAMS.values())  # type: ignore
    response = requests.post(
        url=url, auth=auth, json={"Status": "Работает"}, timeout=61)
    response.raise_for_status()
    drivers_df = pd.DataFrame(response.json())
    drivers_df = drivers_df[
        [
            "MetaId", "DefaultID", "ID", "FIO", "SNILS", "INN",
            "OGRN", "KIS_ART_DriverId", "CarDepartment"
        ]
    ]
    drivers_df = drivers_df[drivers_df["INN"].notnull()]
    drivers_df[["inn_is_valid", "message"]] = \
        [
            validate_inn_12(inn)
            for inn in drivers_df["INN"].tolist()
        ]
    drivers_with_valid_inn = drivers_df[drivers_df["inn_is_valid"]]\
        .sort_values(by=["CarDepartment", "FIO"], ascending=[True, True])

    return drivers_with_valid_inn


def check_statusnpd() -> None:
    """
    Fetch active drivers from 1C:Element, check their
    self-employment status, and update a Google Sheets
    report with the results.
    """
    try:
        active_drivers_df = fetch_active_drivers_with_inn()
        if active_drivers_df.empty:
            logger.info('No drivers with INN found in 1C:Element')
            return None

        logger.info('Checking self-employment status...')
        active_drivers_df = active_drivers_df\
            .drop(columns=["inn_is_valid", "message"])
        active_drivers_df[["is_self_employed", "message", "request_date"]] = \
            [
                check_self_employment_status(inn)
                for inn in active_drivers_df["INN"].tolist()
            ]
        active_drivers_values = active_drivers_df.values.tolist()

        spreadsheet_id, range_name = GOOGLE_SHEETS_PARAMS.values()
        batch_clear_values(spreadsheet_id, range_name)
        batch_update_values(spreadsheet_id, range_name, active_drivers_values)
        logger.info(
            f'Updated Google Sheets {spreadsheet_id} (range: {range_name})'
        )

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Http Error: {http_err}", exc_info=True)

    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"Error Connecting: {conn_err}", exc_info=True)

    except requests.exceptions.Timeout as time_err:
        logger.error(f"Timeout Error: {time_err}", exc_info=True)

    except requests.exceptions.RequestException as err:
        logger.error(f"Unknown request error: {err}", exc_info=True)

    except HttpError as google_err:
        logger.error(
            f'Failed to update {spreadsheet_id}: {google_err}', exc_info=True)


if __name__ == '__main__':
    check_statusnpd()

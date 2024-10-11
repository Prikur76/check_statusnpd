# Checking NPD status for drivers from ERP "Element"  

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Purpose of project](#purpose_of_project)
- [License](#license)

## About <a name = "about"></a>

This program allows you to get information about the presence/absence of the status of a professional income tax payer according to the list of drivers with the status "Working" and if there is a filled-in "TIN" field in the ERP Element driver card.

The results of the check are uploaded to a Google spreadsheet.

To check the status yourself, click on [link](https://npd.nalog.ru/check-status).

## Getting Started <a name = "getting_started"></a>

Make sure that you have configured access to the ERP "Element" via the API with access to the "Drivers" table.

You must have installed python3.

Read the API documentation at this [link](https://npd.nalog.ru/html/sites/www.npd.nalog.ru/api_statusnpd_nalog_ru.pdf):

1. The client must have a response timeout from the server of at least 60 seconds for all API calls,
unless this parameter is specified separately in the description of a specific REST method.
2. There is a ban on the number of requests from one ip address - no more than 2 times in 1 minute.
3. Server responses must be in JSON format.
4. Error codes:
    - 400 - Incorrect request format
    - 422 - Business error (The server was able to process the request, but it cannot be executed either due to incorrect data from the user, or due to technical problems of errors in the execution of this request)
    - 500 - Internal error

### Prerequisites

Create directory and download this repository in any way convenient for you.

For example:

```bash
git clone https://github.com/Prikur76/check_statusnpd.git
```

### Installing

1. Get credentials from the Google Cloud (service account) in json format. Put the file in the root directory.

2. Change variables in the [.env.example](.env.example) file.

3. Create a virtual environment

```bash
python.exe -m venv venv
```

and activate virtual environment (on Windows):

```bash
venv\Scripts\activate
```

if Linux:

```bash
source ./venv/bin/activate
```

Renew pip:

```bash
pip3  install --upgrade pip
```

4. Install dependencies

```bash
pip3 install -r requirements.txt
```

5. Run check

```bash
python main.py
```

## Usage <a name = "usage"></a>

The code can be placed on the server, its execution can be configured via CRON with the necessary frequency.

## Purpose of project <a name = "purpose_of_project"></a>

The project was created for use in the [Next company](taxinext.ru).

## License <a name = "license"></a>

This license is released under the [MIT license](LICENSE).

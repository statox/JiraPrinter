# JiraPrinter
Print your Jira tickets for your Scrum board

# Usage
The application reads configuration from a `config.json` file in its working
diretory:

    {
        "username": "myUserName",
        "password": "MyPassword",
        "host": "JiraHost.com",
        "port": "8080"
    }

It also reads the list of issues to generate from a `issues.txt` file in its
working directory. The file should contain an issue ID by line

    PROJ1-23
    PROJ2-43
    PROJ1-99

# Dependencies
The application uses [pdfKit](https://github.com/JazzCore/python-pdfkit) to
generate PDF from HTML files. This module needs
[wkhtmltopdf](https://wkhtmltopdf.org/) installed to work properly.

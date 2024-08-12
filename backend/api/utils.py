# Модуль бизнес логики проекта.
import csv
import http
import requests
import os
import shutil
from datetime import datetime

from django.conf import settings
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.response import Response

from contacts.models import Donor
from mixplat.models import MixPlat


def string_to_date(value):
    """Метод преобразования строки в дату, установка time-zone."""
    return make_aware(datetime.strptime(value, settings.DATE_FORMAT))


def donor_exists(email):
    """Метод проверки наличия контакта донора в ДБ."""
    return Donor.objects.filter(email=email).exists()


def mixplat_request_handler(request):
    """Метод создания объектов из данных от Mixplat."""
    try:
        mixplat_obj_dict = dict(
            email=request.data["user_email"],
            donat=request.data["amount"],
            custom_donat=request.data["amount_user"],
            payment_method=request.data["payment_method"],
            payment_id=request.data["payment_id"],
            status=request.data["status"],
            user_account_id=request.data["user_account_id"],
            date_created=string_to_date(request.data["date_created"]),
            date_processed=string_to_date(request.data["date_processed"]),
            payment_operator="mixplat",
            currency=request.data["currency"],
        )

        MixPlat.objects.create(**mixplat_obj_dict)

        if donor_exists(request.data["user_email"]) is False:
            Donor.objects.create(request.data["user_email"])

        return Response(dict(result="ok"), status=status.HTTP_200_OK)
    except KeyError:
        return Response(
            dict(result="error", error_description="Internal error"),
            status=status.HTTP_400_BAD_REQUEST,
        )


def get_cloudpayment_data(request):
    """Формирование данных для сериалайзера CloudpaymentsSerializer."""
    # Предлполагаем, что request.data содержит json-объект,
    # т.е. ответ сервиса Cloudpayments при запросе на создании платежа.
    if isinstance(request.data, dict) and "Model" in request.data:
        model = request.data["Model"][0]
        data = {
            "email": model.get("Email"),
            "custom_donat": model.get("Amount"),
            "date_created": model.get("CreatedDateIso"),
            "date_processed": model.get("ConfirmDateIso"),
            "payment_id": model.get("TransactionId"),
            "status": model.get("Status"),
            "payments_operator": model.get("Issuer"),
            "payment_method": model.get("CardType"),
            "user_account_id": model.get("TransactionId"),
            "currency": model.get("Currency"),
        }
        return data
    raise ValueError("Неправильная структура request.data")


def check_cloudpayments_connection():
    """Проверка подключения к api cloudpayments."""
    url = settings.CLOUDPAYMENTS_API_TEST_URL
    headers = {"Content-Type": "application/json"}
    auth = (
        settings.CLOUDPAYMENTS_PUBLIC_ID,
        settings.CLOUDPAYMENTS_API_SECRET,
    )
    response = requests.post(url, headers=headers, auth=auth)
    if response.status_code == http.HTTPStatus.OK:
        return True
    return False


def send_payment_email(email, message):
    """Sending message via Unisender method."""
    url = settings.DEFAULT_CONF["base_url"]

    data = {
        "api_key": settings.DEFAULT_CONF["api_key"],
        "format": "json",
        "email": email,
        "sender_email": settings.DEFAULT_FROM_EMAIL,
        "sender_name": settings.UNISENDER_SENDER_NAME,
        "subject": "Payment information",
        "body": message,
        "list_id": 1,
    }

    response = requests.post(url, data=data)

    if response.status_code != status.HTTP_200_OK:
        print(f"Ошибка при отправке сообщения: {response.status_code}")
    else:
        print("Сообщение успешно отправлено")


def send_request():
    """Отправка запроса на получение контактов доноров от Unisender."""
    response = requests.get(settings.REQUEST_URL)
    if response.status_code != status.HTTP_200_OK:
        raise f"Ошибка при запросе: {response.status_code}"
    return response.json()["result"]["task_uuid"]


def add_contacts(file_url):
    """Добавление доноров в БД из файла, получаемого по ссылке."""
    response = requests.get(file_url)
    if response.status_code == status.HTTP_200_OK:
        directory = "files"
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, "data.csv")

        with open(file_path, "wb") as file:
            file.write(response.content)

        with open(file_path, encoding="utf-8") as csv_file:
            file_reader = csv.reader(csv_file, delimiter=",")
            count = 0
            bulk_list = list()
            for row in file_reader:
                if count != 0 and donor_exists(row) is False:
                    bulk_list.append(Donor(email=row))
                count += 1
            Donor.objects.bulk_create(bulk_list)
            print(f"Добавленно {count - 1} контактов.")

        try:
            shutil.rmtree(directory)  # удаляем папку с файлом
        except OSError as e:
            raise f"Error: {e.filename, e.strerror}"

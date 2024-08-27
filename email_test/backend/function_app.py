import azure.functions as func
import logging
import requests
import json
from azure.communication.email import EmailClient

API_KEY = '012c76cca6f900121b52a9675092d880'  # OpenWeather APIキーを設定

app = func.FunctionApp()

@app.function_name(name="http_trigger")
@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
def check_weather(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request to check weather.')

    try:
        req_body = req.get_json()
        first_name = req_body.get('firstName', '')
        last_name = req_body.get('lastName', '')
        city = req_body['city']
        to_address = req_body['email']

        name = f"{first_name} {last_name}".strip()

        # OpenWeather APIを呼び出して天気情報を取得
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
        response = requests.get(weather_url)
        weather_data = response.json()

        if response.status_code != 200 or 'main' not in weather_data or 'weather' not in weather_data:
            return func.HttpResponse(
                json.dumps({'message': '天気情報を取得できませんでした。'}),
                status_code=400,
                mimetype="application/json"
            )

        temperature = weather_data['main']['temp']
        weather_description = weather_data['weather'][0]['description']

        # メール本文を作成
        email_message = f"""
        Weather Information:
        City: {city}
        Weather: {weather_description}
        Temperature: {temperature}°C
        """

        # Azure Communication Services (ACS) Emailを使用してメールの送信
        connection_string = "endpoint=https://email0824001.japan.communication.azure.com/;accesskey=65VbEvQcLgkfnPKe8kTMupiiCcqXuS5MXg0nEeuycU925saEgvPeJQQJ99AHACULyCpmk6mxAAAAAZCSRvsd"
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": "DoNotReply@b11ea8d3-d602-4731-a5ea-4da6e003f80b.azurecomm.net",
            "recipients": {
                "to": [{"address": to_address}],
            },
            "content": {
                "subject": "Weather Information",
                "plainText": email_message,
            }
        }

        try:
            poller = client.begin_send(message)
            result = poller.result()

            return func.HttpResponse(
                json.dumps({
                    'message': '天気情報を送信しました！',
                    'temperature': temperature,
                    'weather': {
                        'description': weather_description
                    }
                }),
                status_code=200,
                mimetype="application/json"
            )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({'message': 'メール送信に失敗しました。', 'error': str(e)}),
                status_code=500,
                mimetype="application/json"
            )

    except ValueError as e:
        return func.HttpResponse(
            json.dumps({'message': 'リクエストの処理中にエラーが発生しました。', 'error': 'HTTP request does not contain valid JSON data'}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({'message': 'リクエストの処理中にエラーが発生しました。', 'error': str(e)}),
            status_code=400,
            mimetype="application/json"
        )

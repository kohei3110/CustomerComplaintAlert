from azure.communication.email import EmailClient

from datetime import datetime


class EmailService:


    def __init__(self, connection_string):
        self.email_client = EmailClient.from_connection_string(connection_string)

    def send_email(self, complaint):
        iso_date = complaint["date"]
        # 日付文字列をdatetimeオブジェクトに変換
        date_obj = datetime.fromisoformat(iso_date)
        formatted_date = f"{date_obj.month}月{date_obj.day}日{date_obj.hour}時{date_obj.minute}分"
        message = {
            # FIXME: 送信元アドレスを環境変数から取得する
            "senderAddress": "DoNotReply@12235659-377d-4f35-9e44-9528d57b475c.azurecomm.net",
            "recipients": {
                "to": [
                        {"address": "koheisaito@microsoft.com"},
                    ],
                "cc": [
                        {"address": "Masaya.Oka@microsoft.com"},
                        {"address": "Yunjia.Tang@microsoft.com"},
                        {"address": "kkanazawa@microsoft.com"},
                ],
            },
            "content": {
                "subject": "demo - お客様からの苦情が受信されました。",
                "plainText": f"{complaint["customer"]} 様からの苦情が受信されました。詳細を確認してください。 クレームID: {complaint["id"]} クレーム内容: {complaint["complaint"]} 販売パートナー: {complaint["partner"]} お客様名: {complaint["customer"]} 対象製品: {complaint["product"]} 日付: {formatted_date}",
                "html": f"""
				<html>
					<body>
						<h1>{complaint["customer"]} 様からの苦情が受信されました。詳細を確認してください。</h1>
                        <table>
                            <tr>
                                <th>クレームID</th>
                                <td>{complaint["id"]}</td>
                            </tr>
                            <tr>
                                <th>クレーム内容</th>
                                <td>{complaint["complaint"]}</td>
                            </tr>
                            <tr>
                                <th>販売パートナー</th>
                                <td>{complaint["partner"]}</td>
                            </tr>
                            <tr>
                                <th>お客様名</th>
                                <td>{complaint["customer"]}</td>
                            </tr>
                            <tr>
                                <th>対象製品</th>
                                <td>{complaint["product"]}</td>
                            </tr>
                            <tr>
                                <th>日付</th>
                                <td>{formatted_date}</td>
                            </tr>
					</body>
				</html>"""
            },
            
        }
        try:
            poller = self.email_client.begin_send(message)
            result = poller.result()
            print(f"Email sent: {result}")
        except Exception as e:
            print(f"Failed to send email to '{complaint['customer']}': {e}.")
import json
import requests
import LineError as e
import io
#from PIL import Image


userId = "Ucba9f7e88fb9476bd086af4b563546df"


CHANNEL_ACCESS_TOKEN = "4Pu8lMmwlmoy1Qo+SjG/wURfVBj2/Dz1Kb/DwECEukvepfmVDLK1xZr27d3skqEWZfoiwRsbjqWo7GP+LNKMId5rxghiQ9Ri4mnuR0W4xaCOH9f3B4tFhIoTEbv3Xsx5i4y3pLhjO7ba6kCzd6011AdB04t89/1O/w1cDnyilFU="


class Line:
    def __init__(self, CHANNEL_ACCESS_TOKEN):
        self.CHANNEL_ACCESS_TOKEN = CHANNEL_ACCESS_TOKEN
        self.headers = {
            "Content-Type": "application/json; charset=UTF-8",
            'Authorization': 'Bearer ' + CHANNEL_ACCESS_TOKEN
        }
        self.endpoint = "https://api.line.me/v2/bot/"

    def _request(self, data, method):
        url = self.endpoint + "message/" + method
        result = requests.post(
            url, data=json.dumps(data), headers=self.headers)
        if result.status_code != 200:
            raise e.LineError(result.text)
        return result.text

    def _content(self, id):
        url = self.endpoint + "message/{0}/content".format(id)
        result = requests.get(
            url, headers=self.headers)
        if result.status_code != 200:
            raise e.LineError(result.text)
        return result.content

    def text(self, text, method, to=None, replyToken=None):
        if method == "push":
            for argument in (to, text, method):
                if argument == None:
                    raise e.NoContentError(
                        'No argument "{}" found.'.format(argument))
            data = {"to": to, "messages": [{"type": "text", "text": text}]}
        else:  # method="reply"
            for argument in (replyToken, text, method):
                if argument == None:
                    raise e.NoContentError(
                        'No argument "{}" found.'.format(argument))
            data = {"replyToken": replyToken, "messages": [
                {"type": "text", "text": text}]}
        return self._request(data=data, method=method)

    def sticker(self, packageId, stickerId, method, to=None, replyToken=None):
        if method == "push":
            for argument in (to, packageId, stickerId, method):
                if argument == None:
                    raise e.NoContentError(
                        'No argument "{}" found.'.format(argument))
            data = {"to": to, "messages": [
                {"type": "sticker", "packageId": packageId, "stickerId": stickerId}]}
        else:  # method="reply"
            for argument in (replyToken, packageId, stickerId, method):
                if argument == None:
                    raise e.NoContentError(
                        'No argument "{}" found.'.format(argument))
            data = {"replyToken": replyToken, "messages": [
                {"type": "sticker", "packageId": packageId, "stickerId": stickerId}]}
        return self._request(data=data, method=method)

    def location(self, title, address, latitude, longitude, method, to=None, replyToken=None):
        if method == "push":
            for argument in (to, title, address, latitude, longitude, method):
                if argument == None:
                    raise e.NoContentError(
                        'No argument "{}" found.'.format(argument))
            data = {"to": to, "messages": [{"type": "location", "title": title,
                                            "address": address, "latitude": latitude, "longitude": longitude}]}
        else:  # method="reply"
            for argument in (replyToken, title, address, latitude, longitude, method):
                if argument == None:
                    raise e.NoContentError(
                        'No argument "{}" found.'.format(argument))
            data = {"replyToken": replyToken, "messages": [
                {"type": "location", "title": title, "address": address, "latitude": latitude, "longitude": longitude}]}
        return self._request(data=data, method=method)

    def push(self, to, type, text=None, image=None, title=None, address=None, latitude=None, longitude=None, packageId=None, stickerId=None):
        """
        This is a program to send a push message.

        Keyword arguments:
            to -- an Id of user you want to send Line.
            type -- a kind of message you want to send.
                             you can choose "text", "image", "video", "audio", "file", "location", "sticker"

                if type == text:
                    text -- a message you want to send.

　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　if type == location:
                    title -- a name of location.
                    address -- an address of location
                    latitude -- latitude
                    longitude -- longitude

                if type == sticker:
                    packageId -- packageId
                    stampId -- stampId
                    // for more references, see https://developers.line.me/media/messaging-api/sticker_list.pdf
                    """

        if type == "text":
            return self.text(to=to, text=text, method="push")
        elif type == ("sticker" or "stamp"):
            return self.sticker(to=to, packageId=packageId, stickerId=stickerId, method="push")
        elif type == ("location" or "place"):
            return self.location(to=to, title=title, address=address, latitude=latitude, longitude=longitude, method="push")
        elif type == "imagemap":
            return self.imagemap(to=to,)

    def getContent(self, json):
        """
        input -- the data send from Line server.
        output -- the content of input
        """
        events = json["events"][0]
        result = {}
        replyToken = events["replyToken"]
        result["replyToken"] = replyToken
        userId = events["source"]["userId"]
        result["userId"] = userId
        message = events["message"]
        type = message["type"]
        result["type"] = type
        if type == "text":
            result["text"] = message["text"]
        elif type == "sticker":
            result["stickerId"] = message["stickerId"]
            result["packageId"] = message["packageId"]
        elif type == ("image" or "audio" or "video"):
            result[type] = self._content(message["id"])

        return result


if __name__ == "__main__":
    api = Line(CHANNEL_ACCESS_TOKEN)
    #print(api.push(to=userId, type="sticker", packageId=1327382, stickerId=13199053))
    """
    message = {"type": "imagemap", "baseUrl": "https://olkcomp.sakura.ne.jp/test/", "altText": "This is an imagemap", "baseSize": {"height": 1040, "width": 1040}, "actions": [
        {"type": "uri", "linkUri": "http://comp.olk.jp", "area": {"x": 0, "y": 0, "width": 520, "height": 1040}}, {"type": "message", "text": "Hello", "area": {"x": 520, "y": 0, "width": 520, "height": 1040}}]}
        """
    """
    message={
  "type": "template",
  "altText": "this is a confirm template",
  "template": {
      "type": "confirm",
      "text": "Are you sure?",
      "actions": [
          {
            "type": "message",
            "label": "Yes",
            "text": "yes"
          },
          {
            "type": "message",
            "label": "No",
            "text": "no"
          },
      ]
  }
}
    """
    message = {
        "type": "template",
        "altText": "this is a carousel template",
        "template": {
            "type": "carousel",
            "columns": [
                {
                    "text": "description",


                    "actions": [
                        {
                            "type": "postback",
                            "label": "Buy",
                            "data": "action=buy&itemid=111"
                        },
                        {
                            "type": "postback",
                            "label": "Add to cart",
                            "data": "action=add&itemid=111"
                        },
                        {
                            "type": "uri",
                            "label": "View detail",
                            "uri": "http://example.com/page/111"
                        }
                    ]
                }
            ],
            "imageAspectRatio": "rectangle",
            "imageSize": "cover"
        }
    }

    messages = [message]
    print(messages)
    data = {"to": userId, "messages": messages}
    api._request(data=data, method="push")
    """
    imgByte=api._content(8007785123163)
    print(imgByte)
    print(type(imgByte))
    #print(imgByte)
    with open("aaa.m4a","wb") as img:
        img.write(imgByte)
        """

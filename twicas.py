import requests
import json
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except:
    pass
import re
import base64
try:
    from PIL import Image
except:
    pass
import io
import keys


clientId = keys.clientId
clientSecret = keys.clientSecret
redirect_uri = keys.redirect_uri
twid = keys.twid
twpw = keys.twpw


driver_path = keys.driver_path


class API:
    def __init__(self, id, secret, redirect_uri, is_token=False):
        self.base = "https://apiv2.twitcasting.tv/"
        self.id = id
        self.secret = secret
        self.redirect_uri = redirect_uri
        self.is_token = is_token

        if self.is_token:
            self.token = self.getAccessToken(
                self.id, self.secret, self.redirect_uri)

    def getAccessToken(self, id, secret, redirect_uri):
        options = Options()
        # options.add_argument("--headless")
        driver = webdriver.Chrome(driver_path, chrome_options=options)
        driver.implicitly_wait(2)
        driver.get(
            "https://apiv2.twitcasting.tv/oauth2/authorize?client_id={}&response_type=token".format(id))
        links = driver.find_element_by_link_text("ログイン").click()
        driver.find_element_by_name(
            "session[username_or_email]").send_keys(email)
        driver.find_element_by_name("session[password]").send_keys(pw)
        driver.find_element_by_id("allow").click()
        driver.find_element_by_xpath(
            "//form[@action='https://apiv2.twitcasting.tv/authorize/confirm']").click()

        url = driver.current_url
        token = re.search(r"access_token=(.*?)&", url).groups()[0]
        return token

    def request(self, endpoint, method="GET", params=None):

        url = self.base + endpoint
        header = {"X-Api-Version": "2.0"}
        if self.is_token:
            header["Authorization"] = self.token
        else:
            auth = "{0}:{1}".format(self.id, self.secret)
            auth_e = base64.b64encode(auth.encode("utf-8")).decode()
            header["Authorization"] = "Basic {}".format(auth_e)
        try:
            with requests.Session() as s:
                s.headers.update(header)

                if method == "GET":
                    response = s.get(url, params=params)
                elif method == "DEL":  # DELETE
                    response = s.delete(url, params=params)
                else:  # method=="POST"
                    response = s.post(url, data=json.dumps(
                        params))
        except requests.RequestException as e:
            print(e)
            raise e

        content = response.content
        try:
            if len(content) > 0:
                content = content.decode("utf-8")
                content = json.loads(content)
        except:
            pass

        return content

    def getUserInfo(self, id):
        endpoint = "users/{}".format(id)
        return self.request(endpoint)

    def verifyCredentials(self):
        # ? なにこれ
        endpoint = "verify_credentials"
        return self.request(endpoint)

    def getLiveThumbnailImage(self, id, size="small", position="latest"):
        endpoint = "users/{}/live/thumbnail".format(id)
        params = {"size": size, "position": position}
        return self.request(endpoint, params=params)

    def getMovieInfo(self, id):
        endpoint = "movies/{}".format(id)
        return self.request(endpoint)

    def getMoviesByUser(self, id, offset=0, limit=20):
        endpoint = "users/{}/movies".format(id)
        params = {"offset": offset, "limit": limit}
        return self.request(endpoint, params=params)

    def getCategories(self, lang="ja"):
        params = {"lang": lang}
        endpoint = "categories"
        return self.request(endpoint, params=params)

    def searchLiveMovies(self, type="new", limit=10, context=None, lang="ja"):
        endpoint = "search/lives"
        params = {"limit": limit, "type": type,
                  "context": context, "lang": lang}
        return self.request(endpoint, params=params)

    """
    def lives(self):
        ws=create_connection("wss://{0}:{1}@realtime.twitcasting.tv/lives".format(self.id,self.secret))
        while True:
            print(ws.recv())
            """

    def getWebHookList(self, limit=50, offset=0, id=None):
        endpoint = "webhooks"
        params = {"limit": limit, "offset": offset}
        if id:
            params["user_id"] = id
        return self.request(endpoint, params=params)

    def registerWebHook(self, id, events=["livestart", "liveend"]):
        id = self.getUserInfo(id)["user"]["id"]
        endpoint = "webhooks"
        params = {"user_id": id, "events": events}
        return self.request(endpoint, params=params, method="POST")

    def removeWebHook(self, id, events=["livestart", "liveend"]):
        id = self.getUserInfo(id)["user"]["id"]
        endpoint = "webhooks?user_id={0}".format(id)
        for event in events:
            endpoint += "&events[]={}".format(event)
        return self.request(endpoint, method="DEL")


class user:
    def __init__(self, d):
        try:
            d = d["user"]
        except:
            pass
        self.id = d["id"]
        self.screen_id = d["screen_id"]
        self.name = d["name"]
        self.image_url = d["image"]
        self.profile = d["profile"]
        self.level = d["level"]
        self.is_live = d["is_live"]
        self.last_movie_id = d["last_movie_id"]
        self.supporter_count = d["supporter_count"]
        self.supporting_count = d["supporting_count"]
        self.created = d["created"]

    def __repr__(self):
        s = self.name
        s += " @" + self.screen_id
        if self.is_live:
            s += "  ライブ中！"
        s += "\n"
        s += self.profile
        return s


if __name__ == "__main__":

    api = API(clientId, clientSecret, redirect_uri)

    print(api.getUserInfo("rikuta0811_dashsh"))

import requests
import boto3
import os
import json
import twicas
import Line
import keys

def lambda_handler(event,context):
    LINE=Line.Line(Line.CHANNEL_ACCESS_TOKEN)
    s3=boto3.resource("s3")
    bucket=s3.Bucket("bitcoinsystem")
    bucket.download_file("twicas.csv","/tmp/twicas.csv")

    api=twicas.API(keys.clientId, keys.clientSecret, keys.redirect_uri)


    f=open("/tmp/twicas.csv","r")
    db={}
    line=f.readline()
    line=line.strip()

    while line:
        print(line)
        l=line.split(",")
        if len(l)>1:
            db[l[0]]=l[1::]
        line=f.readline()
        line=line.strip()

    f.close()

    try:#cas
        signature=event["signature"]

        movie=event["movie"]
        owner=api.getUserInfo(movie["user_id"])

        listeners=db[owner["user"]["screen_id"]]
        for listener in listeners:
            try:

                contents=["{}さんの配信が始まりました！お見逃しなく！！".format(owner["user"]["name"]),"動画のリンクはこちら\n{}".format(movie["link"])]
                for content in contents:
                    LINE.push(to=listener,type="text",text=content)
            except:
                pass


    except KeyError:#line
        event=LINE.getContent(event)
        owner=event["text"]
        user=event["userId"]

        if (owner=="一覧" or owner=="いちらん"):
            s="現在\n"
            registered=False
            for key in db.keys():
                if user in db[key]:
                    registered=True
                    s+="{0}\n".format(key)

            s+="さんの配信を登録しています。"
            if registered==False:
                s="現在登録している配信はありません。"
            LINE.push(to=user,type="text",text=s)
            return


        try:
            listener=db[owner]
            if user in listener:

                #LINE.text(text="{}さんの通知を削除します。".format(owner),method="reply",replyToken=event["replyToken"])
                ownerName=api.getUserInfo(owner)["user"]["name"]
                LINE.push(to=user,type="text",text="{}さんの通知を削除します。".format(ownerName))
                listener.remove(user)



            else:
                #LINE.text(text="{}さんのキャスを通知します。".format(owner),ethod="reply",replyToken="replyToken")
                LINE.push(to=user,type="text",text="{}さんのキャスを通知します。".format(owner))
                listener.append(user)
            db[owner]=listener
        except KeyError:
            try:
                #LINE.text(text="{}さんのキャスを通知します。".format(owner),ethod="reply",replyToken="replyToken")
                ownerName=api.getUserInfo(owner)["user"]["name"]
                LINE.push(to=user,type="text",text="{}さんのキャスを通知します。".format(ownerName))
                api.registerWebHook(owner,events=["livestart"])
                db[owner]=[user]
            except KeyError:
                LINE.push(to=user,type="text",text="そのidのユーザーは存在しません。")

        f=open("/tmp/twicas.csv","w")
        for key in db.keys():
            s="{0},{1}\n".format(key,",".join(db[key]))
            f.write(s)
        f.close()

        obj=s3.Object("bitcoinsystem","twicas.csv")
        obj.upload_file("/tmp/twicas.csv")




    return db

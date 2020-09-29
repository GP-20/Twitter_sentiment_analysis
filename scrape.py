from dotenv import load_dotenv
import os
import tweepy
import webbrowser
import time
import pandas as pd
import datetime

load_dotenv()
consumer_key=os.environ["API_key"]
consumer_secret=os.environ["API_secret"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

try:
    redirect_url = auth.get_authorization_url()
except tweepy.TweepError:
    print('Error! Failed to get request token.')
    
webbrowser.open(redirect_url) #autorizar la aplicación

pin_number=input("Escribir el pin generado: ") #pin de autorización otorgado por el link anterior

auth.get_access_token(pin_number)

api=tweepy.API(auth)

def limit_handler(cursor):
    """Limitador que permita obtener todos los tweets de la semana
    relacionados con la búsqueda, respetando los límites de los requests 
    permitidos por la API, con un descanso de 15 minutos para volver a 
    reiniciar la extracción de datos 
    """
    i=1
    while i<=100000:
        try:
            print(f"tweet-{i}")
            yield cursor.next()
            i+=1
        except tweepy.error.TweepError:
            descanso=datetime.datetime.now().strftime("%H:%M:%S")
            print(f"Rate limiit iniciado a las {descanso}")
            time.sleep(15*60)
        except StopIteration:
            print("Terminado")
            break
        
query="#AMLO"
tweets=[]

for status in limit_handler(tweepy.Cursor(api.search,q=query,tweet_mode='extended').items()):
    if 'RT @' not in status.full_text and status.lang=="es":
        id_=status.id
        tweet=status.full_text
        fecha=status.created_at
        autor=status.author.screen_name
        dispositivo=status.source
        tweet_completo={"ID":id_,"tweet":tweet,"fecha":fecha,"usuario":autor,"dispositivo":dispositivo}
        tweets.append(tweet_completo)

df=pd.DataFrame(tweets)
first_date=df["fecha"].min().strftime("%d-%m")
time=datetime.datetime.now().strftime("%d-%m")
df.to_csv(f"tweets_{first_date}_to_{time}.csv",index=False)

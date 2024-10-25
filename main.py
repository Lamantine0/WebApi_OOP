
from datetime import  datetime
import imghdr
import json
from typing import Annotated, Optional
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel 
from models_db.model import Table_news
from settings.settings_db import settings_db
from fastapi.responses import JSONResponse
from sqlalchemy import or_
import base64



app = FastAPI()


class News1(BaseModel):
    id: int
    title: str
    news: str
    image: str  

class News:
    
    @app.post("/create_post_news/", tags=["Создание новости"])
    async def create_news(title: str, news: str, date: datetime, image: UploadFile = File(...), time = datetime):
   
        photo_data = await image.read()

        with settings_db.SessionLocal() as db:
            
            current_time = time.now().strftime("%H:%M")

            current_date = date.now().strftime("%Y-%m-%d")

            if date.strftime("%Y-%m-%d") != current_date:
                raise HTTPException(status_code=404, detail="Дата должна быть сегодняшней")

            new_news = Table_news(
            title = title,
            image = photo_data,
            news = news,
        )
                
        if not new_news:
            raise HTTPException(status_code=404, detail="Новость не создана")    
      
        db.add(new_news)
        db.commit()
        db.refresh(new_news)
       
        return {"Новость добавлена : id" : new_news.id,
        "Дата добавления новости" : current_date,
        "Время добавление новости" : current_time}

        
    


    @app.get("/get_all_news/", tags=["Получение всех новостей"])
    async def get_all_news():
        
       with settings_db.SessionLocal() as db:
       
        all_news = db.query(Table_news).all()

        if not all_news:
            raise HTTPException(status_code=404, detail="Новости не найдены")

        
        
        news_list = []

        for news in all_news:

            if isinstance(news.image, bytes):
                
                image_type = imghdr.what(None, news.image)

                #image_base64 = base64.b64encode(news.image).decode('utf-8')
                #image_data = image_base64


            else:
                
                image_type  = None
            
           
            news_item = Table_news(
                id=news.id,
                title=news.title,
                news=news.news,
                image=image_type
            ) 
           
            news_list.append({
                "id": news_item.id,
                "title": news_item.title,
                "news": news_item.news,
                "image": news_item.image
            })

        return news_list
     
 

    @app.delete("/delete_news_by_id/", tags=["Удаление новости по id"])
    async def delete_news_id(id: int):

        db = settings_db.SessionLocal()

        delete_id_news = db.query(Table_news).filter(Table_news.id == id).first()
        
        if delete_id_news is not id :

            raise HTTPException(status_code=500, detail="ID новости не найдено, либо удалено")
            
        

        db.delete(delete_id_news)
        db.commit()
        db.close()

        return ("Новость с id: {id} удалена")
        

        
    @app.get("/get_news_by_id/" , tags=["Получение новости по ID"])
    async def get_news_id(id: int):

        with  settings_db.SessionLocal() as db:

            news_id = db.query(Table_news).filter(Table_news.id == id).first()

            

            if news_id.image:

                image_base64 = base64.b64encode(news_id.image).decode('utf-8')
                
            

            if news_id is None:
                raise HTTPException(status_code=404, detail="Ошибка, id не найден либо удалён")

                
            
        return {"id" : news_id.id,
                "title" : news_id.title,
                "news" : news_id.news,
                "image" : image_base64
                }

            
            

    @app.get("/get_news_by_title/", tags=["Получение новости по title"])
    async def get_news_by_title(title: str):

        with settings_db.SessionLocal() as db:

            news_title = db.query(Table_news).filter(Table_news.title == title).first()

            if news_title.title is not title:
                raise HTTPException(status_code=404, detail="Новость не найдена")
            
            return {"id" : news_title.id,
                "title" : news_title.title,
                "news" : news_title.news}
                

    class Table_model(BaseModel):

        id: str
        title : str
        news : str                  

    @app.get("/search_news_by_keyword/", response_model=list[Table_model], tags=["Поиск по ключевому слову"])
    async def search_news_by_keyword(keyword: str):

        with settings_db.SessionLocal() as db:

            title_search_by_keyword = db.query(Table_news).filter(
                or_(Table_news.title.like(f"%{keyword}%")
            )).all()
        
        if not title_search_by_keyword:
            raise HTTPException(status_code=404, detail="Ключевое слово не найдено")

        list_news_keyword = []

        for title in title_search_by_keyword:

            list_news_keyword.append({
                "id" : title.id,
                "title" : title.title,
                "news" : title.news

            })

        return JSONResponse(list_news_keyword)
              

        
    @app.put("/change_news/{id}", tags=["Изменение новости по id"])
    async def change_news(
        # обязательный параментр id
        id : int, 
        title : Optional[str] = None, 
        news : Optional[str] = None,
        image: Optional[UploadFile] = None):
        
        with settings_db.SessionLocal() as db:

            news_to_update = db.query(Table_news).filter(Table_news.id == id).first()

            if not news_to_update:
                raise HTTPException(status_code=404, detail="Новость не найдена")

            if title is not None:
                news_to_update.title = title

            if news is not None:
                news_to_update.news = news

            if image is not None:

                photo_data = await image.read()

                news_to_update.image = photo_data

            db.commit()

            return {f"Новость с id : {news_to_update.id} успешно обновлена"}   

            
        



    @app.get("/get_news_date/", tags=["Дата публикации новсти"])
    async def news_data():

        current_date = datetime.now().strftime("%d/%m/%Y")

        current_time = datetime.now().strftime("%H:%M")

        with settings_db.SessionLocal() as db:

            add_news_times = db.query(Table_news).filter().all()

            if not add_news_times:
                raise HTTPException(status_code=404, detail="новость не найдена")  

            list_news = []
            
            for news in add_news_times:

                list_news.append(
                    {   
                        #current_date и current_time не возможно сохранить в объект т.к они не являются частью объекта add_news_times
                        "date" : current_date,
                        "time" : current_time,
                        "id" :  news.id,
                        "title" : news.title, 
                        "news" :  news.news,  

                    }
                )   

            return list_news    
                   
                
    
    @app.get("/get_img_and_id_news", tags=["Полученик картинки и id новости"])
    async def get_img_and_id(id : str):

        with settings_db.SessionLocal() as db:

            get_news = db.query(Table_news).filter(Table_news.id == id).first()

            if not get_news:
                raise HTTPException(status_code=404, detail="ID новости не найден")
            
            if get_news.image:

                image_base64 = base64.b64encode(get_news.image).decode('utf-8')

            return {
                "Id" : get_news.id,
                "image" : image_base64

            }
            


    
           
            


            
            




        
       
   
            


          
            
         
       


from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
import pymysql.cursors
import folium
from django.http import JsonResponse

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='1234',
                             db='mydb',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# Create your views here.
def mt_list(request):
    page = request.GET.get('page', '1')

    with connection.cursor() as cursor:
        sql = "SELECT id, name, title, height FROM mountains"
        cursor.execute(sql)
        result = cursor.fetchall()
        paginator = Paginator(result, 10)
        page_obj = paginator.get_page(page)
        # print(result)

        context = {'data':page_obj}

    return render(request, 'mountains/mt_list.html', context)

def mt_detail(request, id):
    with connection.cursor() as cursor:
        sql = f"""SELECT * FROM mountains, mt_images
                  WHERE mountains.id={id} AND mountains.id = mt_images.mt_id"""
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)

        lat_long = [result[0]['y_coord'], result[0]['x_coord']]
        m = folium.Map(lat_long, zoom_start=14)
        # m = folium.Map(lat_long, zoom_start=12, tiles='Stamen Terrain')

        # folium 한글깨짐 해결 방법 : 아래 명령어 실행 후 서버 재실행
        # sudo pip3 install git+https://github.com/python-visualization/branca.git@master
        text = "<b>"+result[0]['name']+"</b></br><i>"+result[0]['title']+"</i></br>"

        popText = folium.Html(text+str(lat_long), script=True)
        popup = folium.Popup(popText, max_width=2650)
        folium.Marker(location=lat_long, popup=popup).add_to(m)
        m=m._repr_html_() #updated

        context = {'data':result, 'mountain_map': m}

    return render(request, 'mountains/mt_detail.html', context)


def mt_map(request):

    page = request.GET.get('page', '1')

    with connection.cursor() as cursor:
        sql = "SELECT * FROM mountains"
        cursor.execute(sql)
        results = cursor.fetchall()
        # print(results)
        paginator = Paginator(results, 10)
        page_obj = paginator.get_page(page)

        # folium
        m = folium.Map([35.95, 128.00], zoom_start=7)       # 우리나라 중심 좌표 : [35.95, 128.25]

        for result in results:
            lat_long = [result['y_coord'], result['x_coord']]
            # print(lat_long)
            # m = folium.Map(lat_long, zoom_start=12, tiles='Stamen Terrain')

            # folium 한글깨짐 해결 방법 : 아래 명령어 실행 후 서버 재실행
            # sudo pip3 install git+https://github.com/python-visualization/branca.git@master
            text = "<b>"+result['name']+"</b><br><i>"\
                        +result['title']+"</i><br>"\
                        +result['y_coord']+"<br>"\
                        +result['x_coord']+"<br>"

            popText = folium.Html(text, script=True)
            popup = folium.Popup(popText, max_width=150)
            folium.RegularPolygonMarker(location=lat_long,
                                        popup=popup,
                                        number_of_sides=3,
                                        rotation=30,
                                        radius=7).add_to(m)

        m = m._repr_html_() #updated

        context = {'data':page_obj, 'mountain_map': m}
        # context = {'mountain_map': m}

    return render(request, 'mountains/mt_map.html', context)


def listajax(request):

    with connection.cursor() as cursor:
        sql = "SELECT * FROM mountains"
        cursor.execute(sql)
        results = cursor.fetchall()

        #number of items on each page
        number_of_item = 10
        #Paginator
        paginator = Paginator(results, number_of_item)
        #query_set for first page
        first_page = paginator.page(1)
        #range of page ex range(1, 3)
        page_range = paginator.page_range


        # folium
        m = folium.Map([35.95, 128.00], zoom_start=7)       # 우리나라 중심 좌표 : [35.95, 128.25]

        for result in results:
            lat_long = [result['y_coord'], result['x_coord']]
            # print(lat_long)
            # m = folium.Map(lat_long, zoom_start=12, tiles='Stamen Terrain')

            # folium 한글깨짐 해결 방법 : 아래 명령어 실행 후 서버 재실행
            # sudo pip3 install git+https://github.com/python-visualization/branca.git@master
            text = "<b>"+result['name']+"</b><br><i>"\
                        +result['title']+"</i><br>"\
                        +result['y_coord']+"<br>"\
                        +result['x_coord']+"<br>"

            popText = folium.Html(text, script=True)
            popup = folium.Popup(popText, max_width=150)
            folium.RegularPolygonMarker(location=lat_long,
                                        popup=popup,
                                        number_of_sides=3,
                                        rotation=30,
                                        radius=7).add_to(m)

        m = m._repr_html_() #updated

        context = {
        'paginator':paginator,
        'first_page':first_page,
        'page_range':page_range,
        'mountain_map':m
        }

        if request.method == 'POST':
            page_n = request.POST.get('page_n', None) #getting page number
            # results = list(paginator.page(page_n))
            results = list(paginator.page(page_n))
            return JsonResponse({"results":results})



    return render(request, 'mountains/mt_map_ajax.html', context)

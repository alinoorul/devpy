import PyPDF2
import os
import json
import shutil

def create_indexpage(pages):
    k=''
    for i in range(len(pages)):
        k+='<a href='+pages[i]['html_title']+".html style='font-family:consolas;'>"+pages[i]['title']+'</a><br>'
    template = f"""<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="shortcut icon" type="image/x-icon" href="assets/favicon.ico">
        <link rel="stylesheet" href="styles.css">
        <title>The Matrix Dex</title>
    </head>
    <body>
        <br><h1>THE MATRIX DEX</h1><br>
        {k}
        <br><br><br><br><br><br><br>
        <h3><a href="index.html">THE MATRIX</a></h3>
    </body>
    </html>
    """
    return template

def create_webpage(slide_number, title, body):
    k=''
    for i in body:
        k+='<p>'+i+'</p>'
    template = f"""<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="shortcut icon" type="image/x-icon" href="assets/favicon.ico">
        <link rel="stylesheet" href="styles.css">
        <title>{title} - The Matrix Dex</title>
    </head>
    <body>
    <br>
    <h1>{title.upper()}</h1>
    <br>
    {k}
    <br><br><br><br><br><br><br>
    <h3><a href="index.html">THE MATRIX</a></h3>
</body>
</html>"""
    return template

def save_webpages(site_folder_path,assets_path,styles_path,pages):
    if 'assets' not in os.listdir(site_folder_path):
        os.mkdir(site_folder_path+'assets//')
    assets=[]
    for i in os.listdir(assets_path):
        shutil.copy(assets_path+"\\"+i,site_folder_path+"\\assets\\")
    shutil.copy(styles_path,site_folder_path)
    for i in pages:
        with open(site_folder_path+i['html_title']+'.html', "w+", encoding="utf-8") as file:
            file.write(i['page'])

def json_to_webpages(json_file):
    with open(json_file, 'r') as f:
        z=f.read()
    p=json.loads(z)
    titles=[]
    pages=[]
    for i in range(len(p)):
        t2="".join(x for x in p[i]['title'] if x.isalnum())
        t2=t2.lower()
        page=create_webpage(i+1, p[i]['title'], p[i]['body'])
        if len(p[i]['body'])>0:
            pages.append({'title':p[i]['title'], 'page':page, 'html_title': t2})

    pages = sorted(pages, key=lambda x: x['title'])
    pages.append({'title':'The Matrix Dex', 'page':create_indexpage(pages) , 'html_title': 'index'})
    return pages

def pdf_to_json(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    data=[] # list of pages if this was new dex
    for i in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[i]
        text = page.extract_text()
        lines = text.split("\n")
        body = lines[1:]  # Rest of the lines form the body
        title=lines[0]
        data.append({'title':title, 'body':body})
    return data

def txt_to_json(txt_path):
    with open(txt_path, 'r') as f:
        z=f.read()
        z=z.split('\n')
    title=os.path.basename(txt_path)
    title=title[:title.find('.')]
    p=[]
    for i in z:
        if len(i)!=0:
            p.append(i)
    return {'title':title, 'body': p}
    
def pdf_to_webpages(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file,site_folder_path)
    titles=[]
    for i in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[i]
        text = page.extract_text()
        lines = text.split("\n")
        title = lines[0].strip()  # First line is considered as the title
        body = lines[1:]  # Rest of the lines form the body
        
        create_webpage(i+1, p[i]['title'], p[i]['body'])

def get_html_filenames(folder_path):
    filenames=os.listdir(folder_path)
    f=[]
    for i in filenames:
        if len(i)>=5 and i[-5]=='.' and i[-4]=='h' and i[-3]=='t' and i[-2]=='m' and i[-1]=='l':
            f.append(i)
    filenames=f
    return filenames

def html_to_json(site_folder_path):
    data=[]
    raw_html_files=[]
    html_files=get_html_filenames(site_folder_path)
    for file in html_files:
        datum={'title':'', 'body':[]}
        with open(site_folder_path+file, 'r', encoding="utf8") as f:
            z=f.read()
            raw_html_files.append(z)
    for i in raw_html_files:
        datum={'title':'', 'body':[]}
        t=i.split('<title>')
        k=t[1].split('</title>')[0]
        title=k[0:(k.find('-')-1)]
        datum['title']=title
        op=False
        pl=''
        for j in range(len(i)-2):
            if i[j]=='<':
                if i[j+1] == 'p':
                    op=True
                elif i[j+1] == '/':
                    if i[j+2] == 'p':
                        op=False
                        datum['body'].append(pl)
                        pl=''
            if op:
                pl+=i[j]
        k=[]
        for i in datum['body']:
            if len(i.split('<p>'))==2:
                k.append(i.split('<p>')[1])
            else:
                k.append(i)
        datum['body']=k
        data.append(datum)
    return data

def consolidate_json(json_data):
    complete={}
    for i in json_data:
        if i['title'] in complete.keys():
            for k in i['body']:
                    complete[i['title']].append(k)
        else:
            complete[i['title']]=i['body']
    p=[]
    for i in complete:
        p.append({'title':i, 'body':complete[i]})
    return p

def parse_updates(old_path, update_path):
    update_files = os.listdir(update_path)
    p=[]
    for i in update_files:
        p.append({'format': str(i[i.find('.')+1:]), 'file_path': str(update_path + i)})
    updates = p
    updates_json = []
    for i in updates:
        if i['format']=='pdf':
            updates_json.append(pdf_to_json(i['file_path']))

        elif i['format']=='txt':
            
            updates_json.append(txt_to_json(i['file_path']))
        elif i['format']=='json':
            
            with open(i['file_path'], 'r') as f:
                z=f.read()
            p=json.loads(z)
            for j in p:
                updates_json.append(j)
        
    ## EDIT DUMMY JSON IN JSON EDITOR, SEND IT BACK FOR PARSING

    # k=len(os.listdir(update_path))+1
    # for i in range(len(data)):
    #     with open(dummy_json_folder+str(k+i)+'.json', "w+") as file:
    #         file.write(json.dumps(data[i]))
    
    updates_json=consolidate_json(updates_json)

    with open(old_path, 'r') as f:
        z=f.read()
    old=json.loads(z)
    for i in updates_json:
        old.append(i)
    old=consolidate_json(old)
    return old

def upload(site_folder_path): # add github manager bot
    pass

## CONTROLS

if __name__ == "__main__":
    root='C:\\code\\matrix\\dex\\dex v2\\'

    pdf_file_path = root+"dex.pdf"
    site_folder_path = root+"ge4\\"
    json_file = root+'raw\\data.json'
    assets_path = root+'raw\\assets'
    styles_path = root+'raw\\styles.css'
    update_path = root + 'new\\'
    dummy_json_folder = root + 'dummy_json\\'

    # data = parse_updates(json_file, update_path) 
    # # data = html_to_json(site_folder_path)   
    # new_json_path = site_folder_path + 'raw.json'
    # with open(new_json_path, "w+") as file:
    #     file.write(json.dumps(data, indent=4))

    
    if os.path.exists(json_file):
        pages=json_to_webpages(json_file)
        save_webpages(site_folder_path,assets_path,styles_path,pages)
        print("Webpages created successfully.")
    else:
        print("JSON file does not exist")
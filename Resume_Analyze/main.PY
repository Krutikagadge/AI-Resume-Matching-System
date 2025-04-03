
import os
import requests
import streamlit as st
import pandas as pd
import base64,random
import time,datetime
#libraries to parse the resume pdf files
from pyresparser import ResumeParser
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter
import io,random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import *
import plotly.express as px #to create visualisations at the admin session
import nltk
nltk.download('stopwords')
import pickle
import docx  # Extract text from Word file
import PyPDF2  # Extract text from PDF
import re




def load_job_roles_from_csv(file_path):
    df = pd.read_csv(file_path)
    job_roles = {}
    for index, row in df.iterrows():
        role = row['Category']
        skills = set(str(row['Skills']).split(','))  # Ensure proper parsing
        job_roles[role] = skills
    return job_roles


def get_table_download_link(df,filename,text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# def course_recommender(course_list):
#     st.subheader("**Courses & Certificates Recommendations 🎓**")
#     c = 0
#     rec_course = []
#     no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
#     if isinstance(course_list, str):
#         st.error("❌ Error: course_list should be a list but received a string.")
#         return []
#     random.shuffle(course_list)
#     for c_name, c_link in course_list:
#         c += 1
#         st.markdown(f"({c}) [{c_name}]({c_link})")
#         rec_course.append(c_name)
#         if c == no_of_reco:
#             break
#     return rec_course

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    if not course_list:
        st.error("⚠️ No courses found for this category.")
        return []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)  
    rec_course = []
    for idx, (c_name, c_link) in enumerate(course_list[:no_of_reco], start=1):
        st.markdown(f"({idx}) [{c_name}]({c_link})")
        rec_course.append(c_name)   
    return rec_course




#----------------------------------------------------------------------------------

# Load pre-trained model and TF-IDF vectorizer
svc_model = pickle.load(open('clf.pkl', 'rb'))
tfidf = pickle.load(open('tfidf.pkl', 'rb'))
le = pickle.load(open('encoder.pkl', 'rb'))

# Function to clean resume text
def cleanResume(txt):
    cleanText = re.sub('http\S+\s', ' ', txt)
    cleanText = re.sub('RT|cc', ' ', cleanText)
    cleanText = re.sub('#\S+\s', ' ', cleanText)
    cleanText = re.sub('@\S+', '  ', cleanText)
    cleanText = re.sub('[%s]' % re.escape("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"), ' ', cleanText)
    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)
    cleanText = re.sub('\s+', ' ', cleanText)
    return cleanText

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

# Function to extract text from TXT
def extract_text_from_txt(file):
    try:
        text = file.read().decode('utf-8')
    except UnicodeDecodeError:
        text = file.read().decode('latin-1')
    return text

# Function to handle file upload and extraction
def handle_file_upload(uploaded_file):
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension == 'pdf':
        text = extract_text_from_pdf(uploaded_file)
    elif file_extension == 'docx':
        text = extract_text_from_docx(uploaded_file)
    elif file_extension == 'txt':
        text = extract_text_from_txt(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")
    return text



# Function to predict the category of a resume
def pred(input_resume):
    cleaned_text = cleanResume(input_resume)
    vectorized_text = tfidf.transform([cleaned_text]).toarray()
    predicted_category = svc_model.predict(vectorized_text)
    predicted_category_name = le.inverse_transform(predicted_category)
    return predicted_category_name[0]

#---------------------------------------------------------------------------------





#CONNECT TO DATABASE

connection = pymysql.connect(host='localhost',user='root',password='Abhishek@1801',db='cv')
cursor = connection.cursor()

def insert_data(name, email, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    DB_table_name = 'user_data'
    
    # Updated INSERT statement without resume_score
    insert_sql = """
    INSERT INTO user_data (Name, Email_ID, Timestamp, Page_no, Predicted_Field, User_level, Actual_skills, Recommended_skills, Recommended_courses)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Create the tuple of values to insert
    rec_values = (name, email, timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills, courses)

    # Execute the query
    cursor.execute(insert_sql, rec_values)
    connection.commit()





# # Define user roles
# USER_TYPES = ["Candidate", "Company"]
# st.title("🔍 AI Resume Analyzer & Candidate Scoring")
# # User selects their role
# user_type = st.selectbox("Login as:", USER_TYPES)


def run():
    st.title("🔍 AI Resume Analyzer & Candidate Scoring")
    activities = ["User", "Company"]
    choice = st.selectbox("Login as:", activities)


    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(500) NOT NULL,
                     Email_ID VARCHAR(500) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field BLOB NOT NULL,
                     User_level BLOB NOT NULL,
                     Actual_skills BLOB NOT NULL,
                     Recommended_skills BLOB NOT NULL,
                     Recommended_courses BLOB NOT NULL,
                     PRIMARY KEY (ID));
                    """
    

    #-------------------------------------------------------------------



    #--------------------------------------------------------------------
    cursor.execute(table_sql)
    if choice == 'User':
        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload your resume, and get smart recommendations</h5>''',
                    unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        

        if pdf_file is not None:
            with st.spinner('Uploading your Resume...'):
                time.sleep(4)
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
        if pdf_file is not None:
        # Extract text from the uploaded file
            try:
                resume_text = handle_file_upload(pdf_file)
                st.write("Successfully extracted the text from the uploaded resume.")


                # Make prediction
                st.subheader("Predicted Category")
                category = pred(resume_text)
                st.write(f"The predicted category of the uploaded resume is: **{category}**")

            except Exception as e:
                st.error(f"Error processing the file: {str(e)}")
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Your Basic info**")
                
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                keywords = st_tags(label='### Your Current Skills',
                text='See our skills recommendation below',
                    value=resume_data['skills'],key = '1  ')
            
                # if resume_data['no_of_pages'] == 1:
                #     cand_level = "Fresher"
                #     st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                # elif resume_data['no_of_pages'] == 2:
                #     cand_level = "Intermediate"
                #     st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                # elif resume_data['no_of_pages'] >=3:
                #     cand_level = "Experienced"
                #     st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
    

                # st.subheader("**Skills Recommendation💡**")
                ## Skill shows
                
                

                ##  keywords
                category_keywords = {
                "ds_keyword" : ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit'],  
                "hr_keyword" : ['recruitment', 'talent acquisition', 'performance management', 'employee engagement', 'training', 'hr analytics', 'compensation', 'benefits', 'r', 'accounting', 'excel', 'java'] ,
                "arts_keyword" : ['social media', 'graphic design', 'illustration', 'adobe photoshop', 'adobe illustrator', 'content creation']  ,
                "web_keyword" : ['react', 'django', 'node.js', 'react.js', 'php', 'laravel', 'wordpress', 'javascript', 'angular', 'sql', 'r', 'java'] ,
                "mechanical_keyword" : ['r', 'excel', 'cad', 'solidworks', 'ansys', 'manufacturing', 'thermal engineering']  ,
                "sales_keyword" : ['sql', 'excel', 'lead generation', 'crm', 'negotiation', 'market analysis']  ,
                "health_fitness_keyword" : ['market research', 'excel', 'nutrition', 'exercise science', 'health coaching']  ,
                "civil_keyword" : ['excel', 'autocad', 'structural engineering', 'construction', 'estimation']  ,
                "java_dev_keyword" : ['java', 'spring', 'hibernate', 'sql', 'javascript', 'angular', 'social media', 'network security', 'switching', 'routing', 'excel'],  
                "business_analyst_keyword" : ['sql', 'javascript', 'accounting', 'excel', 'java', 'data analysis', 'market research', 'forecasting']  ,
                "sap_dev_keyword" : ['sap', 'abap', 'hana', 'python', 'sql', 'excel', 'java']  ,
                "automation_testing_keyword ": ['selenium', 'pytest', 'unittest', 'python', 'sql', 'javascript', 'excel', 'java', 'machine learning', 'vpn']  ,
                "electrical_eng_keyword" : ['r', 'budgeting', 'power systems', 'circuit design', 'embedded systems']  ,
                "operations_manager_keyword" :['r', 'accounting', 'sql', 'supply chain', 'process optimization', 'logistics']  ,
                "python_dev_keyword" : ['python', 'sql', 'tensorflow', 'flask', 'numpy', 'django', 'excel', 'java', 'pandas', 'angular', 'git']  ,
                "devops_keyword" : ['python', 'sql', 'cloud computing', 'javascript', 'accounting', 'budgeting', 'forecasting', 'java', 'machine learning', 'angular', 'vpn', 'git', 'docker', 'kubernetes', 'jenkins']  ,
                "network_security_keyword" : ['dns', 'python', 'r', 'routing', 'accounting', 'network security', 'lan', 'firewall', 'wan', 'switching', 'vpn']  ,
                "pmo_keyword" : ['budgeting', 'excel', 'forecasting', 'project management', 'risk analysis']  ,
                "database_keyword" : ['derivatives', 'python', 'sql', 'r', 'accounting', 'java', 'machine learning', 'database design', 'oracle', 'mongodb', 'postgresql']  ,
                "hadoop_keyword" : ['hadoop', 'big data', 'python', 'sql', 'r', 'javascript', 'forecasting', 'java', 'machine learning', 'git', 'spark', 'hive', 'mapreduce'] , 
                "etl_dev_keyword" : ['sql', 'etl', 'data pipeline', 'data warehousing', 'data integration']  ,
                "dotnet_dev_keyword" : ['sql', 'javascript', 'accounting', 'excel', 'angular', 'git', 'c#', '.net', 'asp.net'] , 
                "blockchain_keyword" : ['blockchain', 'social media', 'python', 'react', 'sql', 'cloud computing', 'docker', 'javascript', 'routing', 'django', 'java', 'machine learning', 'angular', 'ethereum', 'solidity'] , 
                "testing_keyword" : ['sql', 'excel', 'java', 'software testing', 'manual testing', 'automated testing', 'selenium', 'test cases', 'qa', 'bug tracking']  ,
                }
                recommended_skills = []
                reco_field = ''
                rec_course = ''
                ## Courses recommendation
                # for category, keywords in category_keywords.items():
                #     if any(skill.lower() in keywords for skill in resume_data['skills']):
                #         reco_field = category
                #         st.success(f"** Our analysis says you are looking for {category} Jobs.**")
                #         recommended_skills = keywords
                #         recommended_keywords = st_tags(label='### Recommended skills for you.',
                #                                     text='Recommended skills generated from System',
                #                                     value=recommended_skills, key=f"rec_{category}")
                #         st.markdown("""
                #         <h4 style='text-align: left; color: #1ed760;'>
                #         Adding these skills to resume will boost🚀 the chances of getting a Job
                #         </h4>
                #         """, unsafe_allow_html=True)
                #         #rec_course = course_recommender(category.lower().replace(" ", "_") + "_course")
                #         rec_course = course_recommender(globals().get(category.lower().replace(" ", "_") + "_course", []))

                        

                    
                #         break


                    #--------------------------------------------------------------------------------------
                courses_dict = {
                                "ds_keyword": ds_course,
                                "web_keyword": web_course,
                                "android_keyword": android_course,
                                "ios_keyword": ios_course,
                                "uiux_keyword": uiux_course,
                                "hr_keyword": hr_course,
                                "arts_keyword": arts_course,
                                "mechanical_keyword": mechanical_course,
                                "sales_keyword": sales_course,
                                "health_fitness_keyword": health_fitness_course,
                                "civil_keyword": civil_course,
                                "java_dev_keyword": java_dev_course,
                                "business_analyst_keyword": business_analyst_course,
                                "sap_dev_keyword": sap_dev_course,
                                "automation_testing_keyword": automation_testing_course,
                                "electrical_eng_keyword": electrical_eng_course,
                                "operations_manager_keyword": operations_manager_course,
                                "python_dev_keyword": python_dev_course,
                                "devops_keyword": devops_course,
                                "network_security_keyword": network_security_course,
                                "pmo_keyword": pmo_course,
                                "database_keyword": database_course,
                                "hadoop_keyword": hadoop_course,
                                "etl_dev_keyword": etl_dev_course,
                                "dotnet_dev_keyword": dotnet_dev_course,
                                "blockchain_keyword": blockchain_course,
                                "testing_keyword": testing_course,
}






                recommended_skills = []
                reco_field = ''
                rec_course = ''

                ## Course Recommendation
                for category, keywords in category_keywords.items():
                    if any(skill.lower() in keywords for skill in map(str.lower, resume_data['skills'])):
                        reco_field = category
                        st.success(f"** Our analysis says you are looking for {category} Jobs.**")

                        recommended_skills = keywords
                        recommended_keywords = st_tags(
                            label='### Recommended skills for you.',
                            text='Recommended skills generated from System',
                            value=recommended_skills,
                            key=f"rec_{category}"
                        )

                        st.markdown("""
                        <h4 style='text-align: left; color: #1ed760;'>
                        Adding these skills to your resume will boost🚀 the chances of getting a Job
                        </h4>
                        """, unsafe_allow_html=True)

                
                        rec_course = course_recommender(courses_dict.get(category, []))
                        break 












                    #-------------------------------------------------------------------------------------------




                
                ## Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)

                ### Resume writing recommendation
                st.subheader("**Resume Tips & Ideas💡**")

                messages = [
    "[+] Great! You have added a Career Objective.",

    "[+] Education section is present.",

    "[+] Your resume includes Skills.",

    "[+] Work Experience/Internship included.",

    "[+] Projects section is included.",

    "[+] Certifications/Achievements are included.",

    "[+] Hobbies/Extracurricular activities are mentioned.",

    "[+] Proper resume formatting detected.",

    "[+] Resume contains relevant job keywords.",

    "[+] Contact information (email, phone) is included.",

    "[+] Professional summary added at the top of the resume.",

    "[+] Your resume has a clear and easy-to-read layout.",

    "[+] Resume includes quantifiable achievements in work experience.",

    "[+] You have included links to your LinkedIn or portfolio.",

    "[+] Your resume has a good balance between content and white space.",

    "[+] You have included a section for references or a statement about references available upon request.",

    "[+] You have used active language and action verbs to describe your experience.",

    "[+] Your resume is tailored to the specific job you're applying for.",

    "[+] You have avoided irrelevant personal details (e.g., age, marital status).",

    "[+] Resume length is appropriate (1-2 pages, depending on experience).",

    "[+] Your resume highlights your soft skills (communication, teamwork, leadership, etc.).",

    "[+] The font size is consistent, and headings stand out.",

    "[+] You have included keywords from the job description to help with applicant tracking systems (ATS).",

    "[+] Your resume is free of spelling and grammatical errors.",

    "[+] You have avoided using generic terms and clichés (e.g., 'hardworking' or 'team player').",

    "[+] Your resume includes professional development activities, such as conferences or workshops.",

    "[+] Your work experience is listed in reverse chronological order, starting with your most recent role.",

    "[+] You have used industry-specific terminology where relevant.",

    "[+] You have kept the resume focused and concise, with no unnecessary filler content."
]

                # Display all messages in Streamlit app as plain text
                for message in messages:
                    st.text(message)

    
                st.balloons()




                insert_data(resume_data['name'], resume_data['email'], timestamp,
                              str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                              str(recommended_skills), str(rec_course))





                

                connection.commit()
            else:
                st.error('Something went wrong..')
    elif choice == "Company":
        st.subheader("🏢 Post a Job & Get Ranked Candidates")
        job_title = st.text_input("Job Title")
        job_description = st.text_area("Job Description")
        job_category = st.selectbox("Select Category:", ["ENGINEERING", "FINANCE", "HR", "SALES"])
        top_n = st.slider("Number of Candidates", 1, 10, 5)

        if st.button("Get Ranked Candidates"):
            # Call API to get ranked candidates
            api_url = "http://127.0.0.1:8000/score_candidates"
            response = requests.post(api_url, json={
                "category": job_category,
                "job_description": job_description,
                "top_n": top_n
            })

            if response.status_code == 200:
                candidates = response.json()
                for candidate in candidates:
                    st.write(f"*Rank {candidate['rank']}* - Score: {candidate['match_score']}")
                    st.write(f"Resume: {candidate['resume_file']}")

                    # Read resume file content for download
                    resume_file_path = os.path.join("raw_resumes", job_category, candidate["resume_file"])
                    
                    if os.path.exists(resume_file_path):
                        with open(resume_file_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()

                        # Provide file content for download
                        st.download_button(
                            label="Download Resume",
                            data=pdf_bytes,
                            file_name=candidate["resume_file"],
                            mime="application/pdf"
                        )
                    else:
                        st.error("❌ Resume file not found.")
        else:
            st.error("❌ Error retrieving candidates. Ensure FastAPI is running.")
run()




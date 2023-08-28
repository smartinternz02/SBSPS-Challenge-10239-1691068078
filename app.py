import json
import joblib 
import plotly 
import numpy as np
import pandas as pd
import plotly.express as px
from flask import Flask, render_template, request,redirect,url_for

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    global data
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        data = pd.read_csv(f.filename)  # Read the CSV file into a DataFrame
        return redirect(url_for('visual'))
    return render_template('index.html')

@app.route("/visual", methods=['GET', 'POST'])
def visual():
    global data
    if request.method == 'POST':
        selected_category = request.form.get('select_cat')
        selected_function = title[selected_category]
        fig = selected_function()
        fig.update_layout(height=800, width=1200)
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return render_template('form.html', plot=plot_json, category=list(title.keys()))  
    return render_template('form.html', plot=None, category=list(title.keys()))

@app.route("/predict",methods=['GET','POST'])
def predict():
    if request.method == 'POST':
        select_gender = request.form['select_gender']
        ssc_p = float(request.form['ssc_p'])
        hsc_p = float(request.form['hsc_p'])
        hsc_s = request.form['hsc_s']
        degree_p = float(request.form['degree_p'])
        degree_t = request.form['degree_t']
        workex = request.form['workex']
        project = int(request.form['project'])
        specialisation = request.form['specialisation']
        
        gender_x = gender_dict[gender]
        hsc_s_x = hsc_s_dict[hsc_s]
        degree_t_x = degree_t_dict[degree_t]
        workex_x = workex_dict[workex]
        specialisation_x = specialisation_dict[specialisation]

        # x_pred = np.array([[gender_x, ssc_p, hsc_p, hsc_s_x, degree_p, degree_t_x, workex_x, project, specialisation_x]])
        # predicted_status = model.predict(x_pred)
        # print(predicted_status)
        if predicted_status >= 0.5:
            prediction = "Congratulations! You are likely to be placed."
        else:
            prediction = "Sorry, you might not be placed."
        return render_template('predict.html',prediction=prediction)
    return render_template('predict.html',prediction = None)

def Gender_Distribution():
    fig = px.pie(data,names='gender',title='Gender Distribution')
    return fig

def Gender_Distribution_by_Count():
    gender=data.groupby(['gender']).size().reset_index(name="Count")
    gender['gender'] = pd.Categorical(gender['gender'],categories=["male","female"],ordered=True)
    gender=gender.sort_values(by=['gender','Count'])
    fig = px.bar(gender,x='gender',y="Count",color='gender',title="Gender Distribution by Count",color_discrete_sequence=['blue','powderblue'],text_auto=True)
    return fig

def Placement_Status_Distribution():
    status = data.groupby(['status']).size().reset_index(name='count')
    status['status'] = pd.Categorical(status['status'],categories=['Placed','Not Placed'],ordered=True)
    status = status.sort_values(by=['status','count'])
    fig = px.bar(status,x='status',y='count',color='status',title="Placement Status Distribution",color_discrete_sequence=['green','red'],text_auto=True)
    return fig

def Specialization_Distribution():
    program = data.groupby(['specialisation']).size().reset_index(name='count')
    program = program.sort_values(by=['count'])
    fig = px.bar(program,x='specialisation',y='count',title="Specialization Distribution",color = 'specialisation',text_auto=True)
    return fig

def Distribution_of_Specialisation():
    program = data.groupby(['specialisation']).size().reset_index(name='count')
    program = program.sort_values(by=['count'])
    fig = px.pie(program,names='specialisation',hole = 0.6)
    fig.update_traces(textposition='inside', textinfo='percent+label',title='Distribution of Specialisation')
    return fig

def Gender_Specialization_and_Status_Interaction(): 
    gender_placement_counts = data.groupby(['gender', 'status']).size().reset_index(name='Count')
    gender_placement_counts['gender'] = pd.Categorical(gender_placement_counts['gender'], categories=['male', 'female'], ordered=True)
    gender_placement_counts = gender_placement_counts.sort_values(by=['gender', 'status'])
    fig = px.line_3d(data, x="gender", y="specialisation",
                 z="status", color="gender",title="Gender, Specialization, and Status Interaction")
    return fig

def Work_Experience_Specialization_and_Status_Interaction():
    fig = px.scatter_3d(data, x = 'workex',
                    y = 'specialisation',
                    z = 'status',
                    color = 'workex',
                    title="Work Experience, Specialization, and Status Interaction")
    return fig

def Gender_Distribution_in_Placed_and_Not_Placed_Categories():
    gender_placement_counts = data.groupby(['gender', 'status']).size().reset_index(name='Count')
    gender_placement_counts['gender'] = pd.Categorical(gender_placement_counts['gender'], categories=['male', 'female'], ordered=True)
    gender_placement_counts = gender_placement_counts.sort_values(by=['gender', 'status'])
    fig = px.bar(
        gender_placement_counts,
        x='gender',
        y='Count',
        color='status',
        barmode='group',
        title='Gender Distribution in Placed and Not Placed Categories',
        color_discrete_sequence=['red','green'],
        text_auto=True
    )
    return fig

def Placement_Status_by_SSC_Percentage():
    ssc=data.groupby(['ssc_p','status']).size().reset_index(name='count')
    ssc['status']=pd.Categorical(ssc['status'],categories=['Placed','Not Placed'],ordered=True)
    fig = px.bar(ssc,x='status',y='ssc_p',color='ssc_p',title="Placement Status by SSC Percentage")
    return fig

def Placement_Status_by_HSC_Percentage():
    hsc=data.groupby(['hsc_p','status']).size().reset_index(name='count')
    fig = px.bar(hsc,x='status',y='hsc_p',color='hsc_p',title = "Placement Status by HSC Percentage")
    return fig

def Placement_Status_by_Degree_Percentage():
    degree_p=data.groupby(['degree_p','status']).size().reset_index(name='count')
    fig = px.bar(degree_p,x='status',y='degree_p',color='degree_p',title="Placement Status by Degree Percentage")
    return fig

def Placement_Status_Comparison_by_Specialization():
    land_placement_counts = data.groupby(['specialisation', 'status']).size().reset_index(name='Count')
    fig = px.bar(
        land_placement_counts,
        x='specialisation',
        y='Count',
        color='status',
        barmode='group',
        color_discrete_sequence=['red','green'],
        text_auto='specialisation',title='Placement Status Comparison by Specialization')
    return fig

def Salary_Distribution_by_Specialization():
    salary_placement_counts = data.groupby(['specialisation', 'salary']).size().reset_index(name='Count')
    fig = px.bar(salary_placement_counts,
        x='specialisation',
        y='Count',
        color='salary',
        # barmode='group',
        title="Salary Distribution by Specialization",
        # color_discrete_sequence=['red','green']
    )
    return fig

def Work_Experience_Distribution_by_Gender():
    exp = data.groupby(['gender','workex']).size().reset_index(name='count')
    exp['gender'] = pd.Categorical(exp['gender'],categories=['male','female'],ordered=True)
    exp =exp.sort_values(by=['gender'])
    fig = px.bar(
        exp,
        x='gender',
        y='count',
        color='workex',
        color_discrete_sequence=['red','blue'],
        title="Work Experience Distribution by Gender"
    )
    return fig

data = None

title = {
         'Gender Distribution':Gender_Distribution,
         "Gender Distribution by Count":Gender_Distribution_by_Count,
         "Placement Status Distribution":Placement_Status_Distribution,
         "Specialization Distribution":Specialization_Distribution,
         "Distribution of Specialisation":Distribution_of_Specialisation,
         "Gender, Specialization, and Status Interaction":Gender_Specialization_and_Status_Interaction,
         "Work Experience, Specialization, and Status Interaction":Work_Experience_Specialization_and_Status_Interaction,
         'Gender Distribution in Placed and Not Placed Categories':Gender_Distribution_in_Placed_and_Not_Placed_Categories,
         "Placement Status by SSC Percentage":Placement_Status_by_SSC_Percentage,
         "Placement Status by HSC Percentage":Placement_Status_by_HSC_Percentage,
         "Placement Status by Degree Percentage":Placement_Status_by_Degree_Percentage,
         "Placement Status Comparison by Specialization":Placement_Status_Comparison_by_Specialization,
         "Salary Distribution by Specialization":Salary_Distribution_by_Specialization,
         "Work Experience Distribution by Gender":Work_Experience_Distribution_by_Gender,
}

gender_dict = {'male': 1, 'female': 0}
hsc_s_dict = {'Commerce': 2, 'Science': 1, 'Arts': 0}
degree_t_dict = {'Sci&Tech': 2, 'Comm&Mgmt': 0, 'Others': 1}
workex_dict = {'No': 0, 'Yes': 1}
specialisation_dict = {'Java': 0, 'python': 4, 'frontend': 3, 'c': 1, 'c++': 2}

# model = joblib.load('GaussianNB.pkl')

if __name__ == '__main__':
    app.run(debug=True)
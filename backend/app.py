from flask import Flask, render_template,request

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/milkentry')
def milkentry():
    return render_template('milkentry.html')

@app.route('/submit_milk',methods=['GET','POST'])
def submit_milk():
    if request.method=='POST':
      animal_id=request.form['animal_id']
      date=request.form['date']
      shift=request.form['shift']
      qty=request.form['qty']
      fat=request.form['fat']
      snf=request.form['snf']

      print(animal_id,date,shift,qty,fat,snf)
      return "Milk Data Saved"
    return "Invalid Request"
if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.db"
db = SQLAlchemy(app)


class ReportOne(db.Model):
    date = db.Column(db.Integer, primary_key=True)
    kchPrev = db.Column(db.Float)
    kchCurr = db.Column(db.Float)
    ecInPrev = db.Column(db.Float)
    ecInCurr = db.Column(db.Float)
    ecOutPrev = db.Column(db.Float)
    ecOutCurr = db.Column(db.Float)
    tankPrev = db.Column(db.Float)
    tankCurr = db.Column(db.Float)


class ReportTwo(db.Model):
    date = db.Column(db.Integer, primary_key=True)
    mainPrev = db.Column(db.Float)
    mainCurr = db.Column(db.Float)
    kchPrev = db.Column(db.Float)
    kchCurr = db.Column(db.Float)
    ecPrev = db.Column(db.Float)
    ecCurr = db.Column(db.Float)
    tankPrev = db.Column(db.Float)
    tankCurr = db.Column(db.Float)
    dlfPrev = db.Column(db.Float)
    dlfCurr = db.Column(db.Float)
    vblPrev = db.Column(db.Float)
    vblCurr = db.Column(db.Float)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/report_kch")
def report_kch():
    reportKey = int(datetime.today().strftime("%d%m%Y"))
    row = db.session.execute(db.select(ReportOne).filter_by(date=reportKey)).scalar_one()
    print(row)
    if row:
        print(row.date, row.kchCurr, row.ecInCurr, row.ecOutCurr, row.tankCurr)
    return render_template("report_kch.html")


@app.route("/submit_kch", methods=["POST"])
def submit_kch():

    kchPrev = float(request.form["kchPrev"]) if request.form["kchPrev"] else 0
    kchCurr = float(request.form["kchCurr"]) if request.form["kchCurr"] else 0
    ecInPrev = float(request.form["ecInPrev"]) if request.form["ecInPrev"] else 0
    ecInCurr = float(request.form["ecInCurr"]) if request.form["ecInCurr"] else 0
    ecOutPrev = float(request.form["ecOutPrev"]) if request.form["ecOutPrev"] else 0
    ecOutCurr = float(request.form["ecOutCurr"]) if request.form["ecOutCurr"] else 0
    tankPrev = float(request.form["tankPrev"]) if request.form["tankPrev"] else 0
    tankCurr = float(request.form["tankCurr"]) if request.form["tankCurr"] else 0

    dateToday = datetime.today()
    formattedToday = dateToday.strftime("%d/%m/%Y")

    dateYesterday = dateToday - timedelta(days=1)
    formattedYesterday = dateYesterday.strftime("%d/%m/%Y")

    totalMLD = (kchCurr - kchPrev) / 1000
    kchOutflow = f"KCH outflow to EC <br>{formattedYesterday} : {kchPrev}<br>{formattedToday} : {kchCurr}<br>Total MLD    : {totalMLD:.3f}"
    totalMLD = (ecInCurr - ecInPrev) / 1000
    ecInflow = f"Electronic City Inflow <br>{formattedYesterday} : {ecInPrev}<br>{formattedToday} : {ecInCurr}<br>Total MLD    : {totalMLD:.3f}"
    totalMLD = (ecOutCurr - ecOutPrev) / 1000
    ecOutflow = f"Electronic City Outflow <br>{formattedYesterday} : {ecOutPrev}<br>{formattedToday} : {ecOutCurr}<br>Total MLD    : {totalMLD:.3f}"

    multiplier = 1.2
    tankLevelPrevMld = tankPrev * multiplier
    tankLevelCurrMld = tankCurr * multiplier
    tankLevelDiffMld = tankLevelCurrMld - tankLevelPrevMld
    tankLevelIncreased = "Increase" if (tankLevelDiffMld >= 0) else "Decrease"
    tankLevel = f"Previous day tank level: <br>{tankPrev}m   ({tankPrev} * {multiplier} = {tankLevelPrevMld:.3f})<br>Present day tank level: <br>{tankCurr}m   ({tankCurr} * {multiplier} = {tankLevelCurrMld:.3f})<br>{tankLevelIncreased} in tank level: <br>{tankLevelCurrMld:.3f} - {tankLevelPrevMld:.3f} = {tankLevelDiffMld:.3f} MLD"

    report = f"Electronic City<br><br>{kchOutflow}<br><br>{ecInflow}<br><br>{ecOutflow}<br><br>{tankLevel}"

    reportKey = int(dateToday.strftime("%d%m%Y"))
    reportOne = ReportOne(
        date=reportKey,
        kchPrev=kchPrev,
        kchCurr=kchCurr,
        ecInPrev=ecInPrev,
        ecInCurr=ecInCurr,
        ecOutPrev=ecOutPrev,
        ecOutCurr=ecOutCurr,
        tankPrev=tankPrev,
        tankCurr=tankCurr,
    )
    db.session.merge(reportOne)
    db.session.commit()

    return report


@app.route("/report_two")
def report_two():
    return render_template("report_two.html")


@app.route("/submit_two", methods=["POST"])
def submit_two():

    mainPrev = float(request.form["mainPrev"]) if request.form["mainPrev"] else 0
    mainCurr = float(request.form["mainCurr"]) if request.form["mainCurr"] else 0
    kchPrev = float(request.form["kchPrev"]) if request.form["kchPrev"] else 0
    kchCurr = float(request.form["kchCurr"]) if request.form["kchCurr"] else 0
    ecPrev = float(request.form["ecPrev"]) if request.form["ecPrev"] else 0
    ecCurr = float(request.form["ecCurr"]) if request.form["ecCurr"] else 0
    tankPrev = float(request.form["tankPrev"]) if request.form["tankPrev"] else 0
    tankCurr = float(request.form["tankCurr"]) if request.form["tankCurr"] else 0
    dlfPrev = float(request.form["dlfPrev"]) if request.form["dlfPrev"] else 0
    dlfCurr = float(request.form["dlfCurr"]) if request.form["dlfCurr"] else 0
    vblPrev = float(request.form["vblPrev"]) if request.form["vblPrev"] else 0
    vblCurr = float(request.form["vblCurr"]) if request.form["vblCurr"] else 0

    dateToday = datetime.today()
    formattedToday = dateToday.strftime("%d/%m/%Y")

    dateYesterday = dateToday - timedelta(days=1)
    formattedYesterday = dateYesterday.strftime("%d/%m/%Y")

    mainTotalMLD = (mainCurr - mainPrev) / 1000
    mainFlow = f"Main Flow at KCH GLR <br>{formattedYesterday} : {mainPrev}<br>{formattedToday} : {mainCurr}<br>Total MLD    : {mainTotalMLD:.3f}"

    kchTotalMLD = (kchCurr - kchPrev) / 1000
    inletKCH = f"Inlet to KCH GLR Tank <br>{formattedYesterday} : {kchPrev}<br>{formattedToday} : {kchCurr}<br>Total MLD    : {kchTotalMLD:.3f}"

    ecTotalMLD = (ecCurr - ecPrev) / 1000
    ecReading = f"Electronic City Reading  <br>{formattedYesterday} : {ecPrev}<br>{formattedToday} : {ecCurr}<br>Total MLD    : {ecTotalMLD:.3f}"

    vblTotalMLD = (vblCurr - vblPrev) / 1000
    vblReading = f"Vijaya Bank Layout Reading  <br>{formattedYesterday} : {vblPrev}<br>{formattedToday} : {vblCurr}<br>Total MLD    : {vblTotalMLD:.3f}"

    multiplier = 3.6
    tankLevelPrevMld = tankPrev * multiplier
    tankLevelCurrMld = tankCurr * multiplier
    tankLevelDiffMld = tankLevelCurrMld - tankLevelPrevMld
    tankLevelIncreased = "Increase" if (tankLevelDiffMld >= 0) else "Decrease"
    tankLevel = f"Previous day tank level: <br>{tankPrev}m   ({tankPrev} * {multiplier} = {tankLevelPrevMld:.3f}) \
                <br>Present day tank level: <br>{tankCurr}m   ({tankCurr} * {multiplier} = {tankLevelCurrMld:.3f}) \
                <br>{tankLevelIncreased} in tank level: <br>{tankLevelCurrMld:.3f} - {tankLevelPrevMld:.3f} = {tankLevelDiffMld:.3f} MLD"

    value = kchTotalMLD - ecTotalMLD - vblTotalMLD - (tankLevelDiffMld)
    sign = "-" if tankLevelDiffMld >= 0 else "+"
    kchflow = f"KCH / VBL Flow <br> {kchTotalMLD:.3f} - {ecTotalMLD:.3f} - {vblTotalMLD:.3f} {sign} {abs(tankLevelDiffMld):.3f} = {value:.3f}"

    dlfTotalMLD = (dlfCurr - dlfPrev) / 1000
    dlfReading = f"DLF Road Reading  <br>{formattedYesterday} : {dlfPrev}<br>{formattedToday} : {dlfCurr}<br>Total MLD    : {dlfTotalMLD:.3f}"

    report = f"{mainFlow}<br><br>{inletKCH}<br><br>{ecReading}<br><br>{vblReading}<br><br>{tankLevel}<br><br>{kchflow}<br><br>{dlfReading}"

    reportKey = int(dateToday.strftime("%d%m%Y"))
    reportTwo = ReportTwo(
        date=reportKey,
        mainPrev=mainPrev,
        mainCurr=mainCurr,
        kchPrev=kchPrev,
        kchCurr=kchCurr,
        ecPrev=ecPrev,
        ecCurr=ecCurr,
        tankPrev=tankPrev,
        tankCurr=tankCurr,
        dlfPrev=dlfPrev,
        dlfCurr=dlfCurr,
        vblPrev=vblPrev,
        vblCurr=vblCurr,
    )
    db.session.merge(reportTwo)
    db.session.commit()

    return report


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

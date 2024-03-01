import subprocess

required_packages = ["Flask", "Flask-SQLAlchemy", "pandas", "openpyxl"]
missing_packages = [
    package
    for package in required_packages
    if not subprocess.run(["pip", "show", package], stdout=subprocess.PIPE).returncode
    == 0
]
if missing_packages:
    subprocess.run(["pip", "install"] + missing_packages)

# ------------------------------------------------------------------------------- #

from flask import Flask, render_template, request, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flowreport.db"
db = SQLAlchemy(app)


getToday = lambda: datetime.today()
getYesterday = lambda: getToday() - timedelta(days=1)
dateToday = lambda: getToday().strftime("%d/%m/%Y")
dateYesterday = lambda: getYesterday().strftime("%d/%m/%Y")


class ReportOne(db.Model):
    dateCurr = db.Column(db.String(10), primary_key=True)
    kchCurr = db.Column(db.Float)
    ecInCurr = db.Column(db.Float)
    ecOutCurr = db.Column(db.Float)
    tankCurr = db.Column(db.Float)


class ReportTwo(db.Model):
    dateCurr = db.Column(db.String(10), primary_key=True)
    mainCurr = db.Column(db.Float)
    kchCurr = db.Column(db.Float)
    ecCurr = db.Column(db.Float)
    vblCurr = db.Column(db.Float)
    tankCurr = db.Column(db.Float)
    dlfCurr = db.Column(db.Float)


@app.route("/")
def index():
    return render_template("index.html")


def export_excel(table, reportName):
    filename = dateToday().replace("/", "") + "_" + reportName + ".xlsx"
    engine = db.engine
    query = db.session.query(table)
    df = pd.read_sql(query.statement, engine)
    df.to_excel(filename, index=False)
    return send_file(filename, as_attachment=True)


@app.route("/export_kch")
def export_kch():
    return export_excel(ReportOne, "report_kch")


@app.route("/export_two")
def export_two():
    return export_excel(ReportTwo, "report_two")


@app.route("/report_kch")
def report_kch():
    dataPrev = (0, 0, 0, 0, 0, 0, 0, 0)
    dataYesterday = ReportOne.query.filter_by(dateCurr=dateYesterday()).first()
    if dataYesterday:
        dataToday = ReportOne.query.filter_by(dateCurr=dateToday()).first()
        if dataToday:
            dataPrev = (
                dataYesterday.kchCurr,
                dataToday.kchCurr,
                dataYesterday.ecInCurr,
                dataToday.ecInCurr,
                dataYesterday.ecOutCurr,
                dataToday.ecOutCurr,
                dataYesterday.tankCurr,
                dataToday.tankCurr,
            )
        else:
            dataPrev = (
                dataYesterday.kchCurr,
                0,
                dataYesterday.ecInCurr,
                0,
                dataYesterday.ecOutCurr,
                0,
                dataYesterday.tankCurr,
            )
    return render_template("report_kch.html", dataPrev=dataPrev)


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

    formattedToday = dateToday()
    formattedYesterday = dateYesterday()

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

    reportOneYesterday = ReportOne(
        dateCurr=formattedYesterday,
        kchCurr=kchPrev,
        ecInCurr=ecInPrev,
        ecOutCurr=ecOutPrev,
        tankCurr=tankPrev,
    )
    db.session.merge(reportOneYesterday)
    db.session.commit()

    reportOneToday = ReportOne(
        dateCurr=formattedToday,
        kchCurr=kchCurr,
        ecInCurr=ecInCurr,
        ecOutCurr=ecOutCurr,
        tankCurr=tankCurr,
    )
    db.session.merge(reportOneToday)
    db.session.commit()

    return report


@app.route("/report_two")
def report_two():
    dataPrev = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    dataYesterday = ReportTwo.query.filter_by(dateCurr=dateYesterday()).first()
    if dataYesterday:
        dataToday = ReportTwo.query.filter_by(dateCurr=dateToday()).first()
        if dataToday:
            dataPrev = (
                dataYesterday.mainCurr,
                dataToday.mainCurr,
                dataYesterday.kchCurr,
                dataToday.kchCurr,
                dataYesterday.ecCurr,
                dataToday.ecCurr,
                dataYesterday.vblCurr,
                dataToday.vblCurr,
                dataYesterday.tankCurr,
                dataToday.tankCurr,
                dataYesterday.dlfCurr,
                dataToday.dlfCurr,
            )
        else:
            dataPrev = (
                dataYesterday.mainCurr,
                0,
                dataYesterday.kchCurr,
                0,
                dataYesterday.ecCurr,
                0,
                dataYesterday.vblCurr,
                0,
                dataYesterday.tankCurr,
                0,
                dataYesterday.dlfCurr,
                0,
            )
    return render_template("report_two.html", dataPrev=dataPrev)


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

    formattedToday = dateToday()
    formattedYesterday = dateYesterday()

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

    reportTwoYesterday = ReportTwo(
        dateCurr=formattedYesterday,
        mainCurr=mainPrev,
        kchCurr=kchPrev,
        ecCurr=ecPrev,
        vblCurr=vblPrev,
        tankCurr=tankPrev,
        dlfCurr=dlfPrev,
    )
    db.session.merge(reportTwoYesterday)
    db.session.commit()

    reportTwoToday = ReportTwo(
        dateCurr=formattedToday,
        mainCurr=mainCurr,
        kchCurr=kchCurr,
        ecCurr=ecCurr,
        vblCurr=vblCurr,
        tankCurr=tankCurr,
        dlfCurr=dlfCurr,
    )
    db.session.merge(reportTwoToday)
    db.session.commit()

    return report


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False)

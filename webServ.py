from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/report_kch")
def report_kch():
    return render_template("report_kch.html")


@app.route("/submit_kch", methods=["POST"])
def submit_kch():

    input1 = float(request.form["input1"]) if request.form["input1"] else 0
    input2 = float(request.form["input2"]) if request.form["input2"] else 0
    input3 = float(request.form["input3"]) if request.form["input3"] else 0
    input4 = float(request.form["input4"]) if request.form["input4"] else 0
    input5 = float(request.form["input5"]) if request.form["input5"] else 0
    input6 = float(request.form["input6"]) if request.form["input6"] else 0
    input7 = float(request.form["input7"]) if request.form["input7"] else 0
    input8 = float(request.form["input8"]) if request.form["input8"] else 0

    dateToday = datetime.today()
    formattedToday = dateToday.strftime("%d/%m/%Y")

    dateYesterday = dateToday - timedelta(days=1)
    formattedYesterday = dateYesterday.strftime("%d/%m/%Y")

    totalMLD = (input2 - input1) / 1000
    kchOutflow = f"KCH outflow to EC <br>{formattedYesterday} : {input1}<br>{formattedToday} : {input2}<br>Total MLD    : {totalMLD:.3f}"
    totalMLD = (input4 - input3) / 1000
    ecInflow = f"Electronic City Inflow <br>{formattedYesterday} : {input3}<br>{formattedToday} : {input4}<br>Total MLD    : {totalMLD:.3f}"
    totalMLD = (input6 - input5) / 1000
    ecOutflow = f"Electronic City Outflow <br>{formattedYesterday} : {input5}<br>{formattedToday} : {input6}<br>Total MLD    : {totalMLD:.3f}"

    multiplier = 1.2
    tankLevelPrevMld = input7 * multiplier
    tankLevelCurrMld = input8 * multiplier
    tankLevelDiffMld = tankLevelCurrMld - tankLevelPrevMld
    tankLevelIncreased = "Increase" if (tankLevelDiffMld >= 0) else "Decrease"
    tankLevel = f"Previous day tank level: <br>{input7}m   ({input7} * {multiplier} = {tankLevelPrevMld:.3f})<br>Present day tank level: <br>{input8}m   ({input8} * {multiplier} = {tankLevelCurrMld:.3f})<br>{tankLevelIncreased} in tank level: <br>{tankLevelCurrMld:.3f} - {tankLevelPrevMld:.3f} = {tankLevelDiffMld:.3f} MLD"

    report = f"Electronic City<br><br>{kchOutflow}<br><br>{ecInflow}<br><br>{ecOutflow}<br><br>{tankLevel}"

    return report


@app.route("/report_two")
def report_two():
    return render_template("report_two.html")


@app.route("/submit_two", methods=["POST"])
def submit_two():

    main_prev = float(request.form["mainPrev"]) if request.form["mainPrev"] else 0
    main_curr = float(request.form["mainCurr"]) if request.form["mainCurr"] else 0
    kch_prev = float(request.form["kchPrev"]) if request.form["kchPrev"] else 0
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

    mainTotalMLD = (main_curr - main_prev) / 1000
    mainFlow = f"Main Flow at KCH GLR <br>{formattedYesterday} : {main_prev}<br>{formattedToday} : {main_curr}<br>Total MLD    : {mainTotalMLD:.3f}"

    kchTotalMLD = (kchCurr - kch_prev) / 1000
    inletKCH = f"Inlet to KCH GLR Tank <br>{formattedYesterday} : {kch_prev}<br>{formattedToday} : {kchCurr}<br>Total MLD    : {kchTotalMLD:.3f}"

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

    return report


if __name__ == "__main__":
    app.run(debug=False)

import re
from datetime import datetime, timedelta


class QuarterSimple:
    fp: str = None
    start: str = None
    end: str = None
    value: float = None
    form: str = None
    frame: str = None
    operatingIncomeLoss: float = None
    incomeTaxExpenseBenefit: float = None
    incomeBeforeIncomeTax: float = None
    incomeBeforeIncomeTaxAndEquityInterest: float = None


class Quarter:
    cy_quarter_name: str = None
    fp_quarter_name: str = None
    start: str = None
    end: str = None
    value: float = None
    operatingIncomeLoss: float = None
    incomeTaxExpenseBenefit: float = None
    incomeBeforeIncomeTax: float = None
    incomeBeforeIncomeTaxAndEquityInterest: float = None

    def __str__(self):
        return f"<Quarter {self.cy_quarter_name} start:{self.start} end:{self.end} value:{self.value} operatingIncomeLoss:{self.operatingIncomeLoss} incomeTaxExpenseBenefit:{self.incomeTaxExpenseBenefit} incomeBeforeIncomeTax:{self.incomeBeforeIncomeTax} incomeBeforeIncomeTaxAndEquityInterest:{self.incomeBeforeIncomeTaxAndEquityInterest} >"

    def __repr__(self):
        return f"<Quarter {self.cy_quarter_name} start:{self.start} end:{self.end} value:{self.value} operatingIncomeLoss:{self.operatingIncomeLoss} incomeTaxExpenseBenefit:{self.incomeTaxExpenseBenefit} incomeBeforeIncomeTax:{self.incomeBeforeIncomeTax} incomeBeforeIncomeTaxAndEquityInterest:{self.incomeBeforeIncomeTaxAndEquityInterest} >"


class YearReport:
    year: int
    fullYear: Quarter = None
    q3: Quarter = None
    q4: Quarter = None
    q1: Quarter = None
    q2: Quarter = None

    def __init__(self, year):
        self.year = year

    def __str__(self):
        return f"<YearReport year:{self.year} full_year:{self.fullYear} q1:{self.q1} q2:{self.q2} q3:{self.getQ3()} q4:{self.q4}>"

    def __repr__(self):
        return f"<YearReport year:{self.year} full_year:{self.fullYear} q1:{self.q1} q2:{self.q2} q3:{self.getQ3()} q4:{self.q4}>"

    def getQ3(self):
        if self.q3 is not None:
            return self.q3

        if (self.q2 is None) or (self.fullYear is None) or (
                self.q1 is None) or (self.q4 is None):
            return None

        q = Quarter()
        q.cy_quarter_name = "Q3"
        q.start = increase_date_by(self.q2.end, 1)
        q.end = self.fullYear.end
        q.value = self.fullYear.value - self.q4.value - self.q1.value - self.q2.value

        self.q3 = q
        return self.q3

    def getQuartersInOrder(self):
        quarter_list = []

        if self.getQ3() is not None:
            quarter_list.append(self.getQ3())

        if self.q2 is not None:
            quarter_list.append(self.q2)

        if self.q1 is not None:
            quarter_list.append(self.q1)

        if self.q4 is not None:
            quarter_list.append(self.q4)

        return quarter_list


def sorted_by_property(list: list[dict], key: str, reverse: bool = True):
    return sorted(list, key=lambda x: x[key], reverse=reverse)


# Get the data with "frame" property only
def filter_frame(list: list[dict]):
    filtered_list = []
    for data in list:
        if "frame" in data:
            filtered_list.append(data)
    return filtered_list


def get_quarter_values(list: list[dict]):
    res = {}

    for data in list:
        print(data)
        cy_year = data['frame']
        quarter = get_quarter(data)

        year = get_year(cy_year)
        quarter_text = get_quarter_text(cy_year)

        if quarter_text == "Q4":
            year = year + 1

        if year not in res:
            res[year] = YearReport(year=year)

        year_report = res[year]

        if quarter_text:
            quarter.cy_quarter_name = quarter_text

            if quarter_text == "Q1":
                year_report.q1 = quarter
            elif quarter_text == "Q2":
                year_report.q2 = quarter
            elif quarter_text == "Q4":
                year_report.q4 = quarter
        else:
            year_report.fullYear = quarter

    return res


def get_year(text: str):
    return int(re.search("(19|20)\d{2}", text).group())


def get_quarter_text(text: str):
    res = re.search("(Q1|Q2|Q3|Q4)", text)
    if res:
        return res.group()
    else:
        return ""


def get_quarter(data: dict):
    start_date = data['start']
    end_date = data['end']
    value = data['val']
    fp_year = data['fp']

    quarter = Quarter()
    quarter.start = start_date
    quarter.end = end_date
    quarter.value = value
    quarter.fp_quarter_name = fp_year

    return quarter


def increase_date_by(text: str, delta: int):
    datetime_object = datetime.strptime(text, '%Y-%m-%d')
    time = datetime_object + timedelta(days=delta)
    return time.strftime('%Y-%m-%d')


def get_sorted_year_report(report_list: dict[YearReport]):
    res_list = []
    for key in report_list.keys():
        res_list.append(report_list[key])
        res_list.sort(key=lambda x: x.year, reverse=True)
    return res_list


def merge_quarter_result(toReport: dict, fromReport: dict, type: int):
    for year in toReport.keys():
        toReportYearReport = toReport[year]
        q1 = toReportYearReport.q1
        q2 = toReportYearReport.q2
        q3 = toReportYearReport.getQ3()
        q4 = toReportYearReport.q4

        if year in fromReport:
            fromReportYearReport = fromReport[year]
            assign_quarter_value(toQuarter=q1, fromQuarter=fromReportYearReport.q1, type=type)
            assign_quarter_value(toQuarter=q2, fromQuarter=fromReportYearReport.q2, type=type)
            assign_quarter_value(toQuarter=q3, fromQuarter=fromReportYearReport.getQ3(), type=type)
            assign_quarter_value(toQuarter=q4, fromQuarter=fromReportYearReport.q4, type=type)


quarter_type_operatingIncomeLoss: int = 0
quarter_type_incomeTaxExpenseBenefit: int = 1
quarter_type_incomeBeforeIncomeTax: int = 2
quarter_type_incomeBeforeIncomeTaxAndEquityInterest: int = 3


def assign_quarter_value(toQuarter: Quarter, fromQuarter: Quarter, type: int):
    if (toQuarter is not None) and (fromQuarter is not None):
        if type == 0:
            toQuarter.operatingIncomeLoss = fromQuarter.value
        elif type == 1:
            toQuarter.incomeTaxExpenseBenefit = fromQuarter.value
        elif type == 2:
            toQuarter.incomeBeforeIncomeTax = fromQuarter.value
        elif type == 3:
            toQuarter.incomeBeforeIncomeTaxAndEquityInterest = fromQuarter.value


def merge_property_value(toList: list, fromList: list, name: str):
    for qDict in toList:
        q = get_simple_quarter(qDict)
        key = q.start + q.end
        q2 = find_quarter(key=key, target=fromList)

        if q2 is not None:
            qDict[name] = q2.value
        else:
            qDict[name] = None


def get_simple_quarter(qDict: dict):
    q = QuarterSimple()
    q.start = qDict['start']
    q.end = qDict['end']
    q.value = qDict['val']
    q.fp = qDict['fp']
    q.form = qDict['form']

    if 'frame' in qDict:
        q.frame = qDict['frame']

    if "Operating Income Loss" in qDict:
        q.operatingIncomeLoss = qDict["Operating Income Loss"]

    if "Income Tax Expense Benefit" in qDict:
        q.incomeTaxExpenseBenefit = qDict["Income Tax Expense Benefit"]

    if "Income Before Income Tax" in qDict:
        q.incomeBeforeIncomeTax = qDict["Income Before Income Tax"]

    if "Income Before Income Tax And EquityInterest" in qDict:
        q.incomeBeforeIncomeTaxAndEquityInterest = qDict["Income Before Income Tax And EquityInterest"]

    return q


def toMillion(num: float):
    if num is None:
        return None

    return f"{int(num / 1000000.0)} M"


def find_quarter(key: str, target: list):
    if target is None:
        return None

    for qDict in target:
        q = get_simple_quarter(qDict)
        my_key = q.start + q.end
        if my_key == key:
            return q
    return None

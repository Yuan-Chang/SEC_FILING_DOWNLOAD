from sec_edgar_api import EdgarClient
import json
from datetime import datetime
from utils.util import filter_frame, get_quarter_values, sorted_by_property, get_sorted_year_report, \
    merge_quarter_result, quarter_type_operatingIncomeLoss, quarter_type_incomeBeforeIncomeTax, \
    quarter_type_incomeBeforeIncomeTaxAndEquityInterest, quarter_type_incomeTaxExpenseBenefit


def get_report_summary(cik: str = "723125", number_of_quarter: int = 10):
    edgar = EdgarClient("<Sample Company Name> <Admin Contact>@<Sample Company Domain>")

    # 723125
    # result = edgar.get_company_facts(cik="6951")

    result = edgar.get_company_facts(cik=cik)

    operatingIncomeLoss = result['facts']['us-gaap']['OperatingIncomeLoss']
    operatingIncomeLossList = result['facts']['us-gaap']['OperatingIncomeLoss']["units"]["USD"]
    taxRate = result['facts']['us-gaap']['EffectiveIncomeTaxRateContinuingOperations']
    taxRateList = result['facts']['us-gaap']['EffectiveIncomeTaxRateContinuingOperations']["units"]["pure"]
    incomeTaxExpenseBenefit = result['facts']['us-gaap']['IncomeTaxExpenseBenefit']
    incomeTaxExpenseBenefitList = result['facts']['us-gaap']['IncomeTaxExpenseBenefit']["units"]["USD"]

    incomeBeforeIncomeTaxList = []
    if 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest' in result['facts'][
        'us-gaap']:
        incomeBeforeIncomeTax = result['facts']['us-gaap'][
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest']
        incomeBeforeIncomeTaxList = result['facts']['us-gaap'][
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest']["units"][
            "USD"]

    incomeBeforeIncomeTaxAndEquityInterestList = []
    if 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments' in \
            result['facts']['us-gaap']:
        incomeBeforeIncomeTaxAndEquityInterest = result['facts']['us-gaap'][
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments']
        incomeBeforeIncomeTaxAndEquityInterestList = result['facts']['us-gaap'][
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments'][
            "units"]["USD"]

    # sort the list
    operatingIncomeLossList = sorted_by_property(operatingIncomeLossList, "end")
    taxRateList = sorted_by_property(taxRateList, "end")
    incomeTaxExpenseBenefitList = sorted_by_property(incomeTaxExpenseBenefitList, "end")
    incomeBeforeIncomeTaxList = sorted_by_property(incomeBeforeIncomeTaxList, "end")
    incomeBeforeIncomeTaxAndEquityInterestList = sorted_by_property(incomeBeforeIncomeTaxAndEquityInterestList, "end")

    # filter data with "frame" property
    operatingIncomeLossList = filter_frame(operatingIncomeLossList)
    taxRateList = filter_frame(taxRateList)
    incomeTaxExpenseBenefitList = filter_frame(incomeTaxExpenseBenefitList)
    incomeBeforeIncomeTaxList = filter_frame(incomeBeforeIncomeTaxList)
    incomeBeforeIncomeTaxAndEquityInterestList = filter_frame(incomeBeforeIncomeTaxAndEquityInterestList)

    operatingIncomeLossYearReport = get_quarter_values(operatingIncomeLossList)
    incomeTaxExpenseBenefitYearReport = get_quarter_values(incomeTaxExpenseBenefitList)
    incomeBeforeIncomeTaxYearReport = get_quarter_values(incomeBeforeIncomeTaxList)
    incomeBeforeIncomeTaxAndEquityInterestYearReport = get_quarter_values(incomeBeforeIncomeTaxAndEquityInterestList)

    merge_quarter_result(toReport=operatingIncomeLossYearReport, fromReport=operatingIncomeLossYearReport,
                         type=quarter_type_operatingIncomeLoss)
    merge_quarter_result(toReport=operatingIncomeLossYearReport, fromReport=incomeTaxExpenseBenefitYearReport,
                         type=quarter_type_incomeTaxExpenseBenefit)
    merge_quarter_result(toReport=operatingIncomeLossYearReport, fromReport=incomeBeforeIncomeTaxYearReport,
                         type=quarter_type_incomeBeforeIncomeTax)
    merge_quarter_result(toReport=operatingIncomeLossYearReport,
                         fromReport=incomeBeforeIncomeTaxAndEquityInterestYearReport,
                         type=quarter_type_incomeBeforeIncomeTaxAndEquityInterest)

    res_list = []
    for key in operatingIncomeLossYearReport.keys():
        res_list.append(operatingIncomeLossYearReport[key])
    res_list.sort(key=lambda x: x.year, reverse=True)

    quarter_number = number_of_quarter
    count = 0
    for yearReport in res_list:
        quarter_list = yearReport.getQuartersInOrder()

        for quarter in quarter_list:
            count = count + 1

            # print
            print(f"{quarter.cy_quarter_name}({quarter.start} to {quarter.end})")
            print(f"---------------------------")
            print(f"operatingIncomeLoss: {quarter.operatingIncomeLoss}")
            print(f"incomeTaxExpenseBenefit: {quarter.incomeTaxExpenseBenefit}")
            print(f"incomeBeforeIncomeTax: {quarter.incomeBeforeIncomeTax}")
            print(f"incomeBeforeIncomeTaxAndEquityInterest: {quarter.incomeBeforeIncomeTaxAndEquityInterest}")
            print(f"\n")

            if count == quarter_number:
                break

        if count == quarter_number:
            break


company_dict = {"MU": "723125"}

for name in company_dict:
    cik = company_dict[name]
    print(f"Name:{name} cik:{cik}")
    print(f"=======================================")
    get_report_summary(cik=cik, number_of_quarter=12)

# for year in operatingIncomeLossYearReport.keys():
#     incomeTaxExpenseBenefitYear = incomeTaxExpenseBenefitYearReport[year]
#     q1 = incomeTaxExpenseBenefitYear.q1
#     q2 = incomeTaxExpenseBenefitYear.q2
#     q3 = incomeTaxExpenseBenefitYear.getQ3()
#     q4 = incomeTaxExpenseBenefitYear.q4
#
#     if year in incomeBeforeIncomeTaxYearReport:
#         incomeBeforeIncomeTaxYearReportYear = incomeBeforeIncomeTaxYearReport[year]
#
#         if (q1 is not None) and (incomeBeforeIncomeTaxYearReportYear.q1 is not None):
#             q1.incomeBeforeIncomeTax = incomeBeforeIncomeTaxYearReportYear.q1.incomeBeforeIncomeTax
#
#         if (q2 is not None) and (incomeBeforeIncomeTaxYearReportYear.q2 is not None):
#             q2.incomeBeforeIncomeTax = incomeBeforeIncomeTaxYearReportYear.q2.incomeBeforeIncomeTax
#
#         if (q3 is not None) and (incomeBeforeIncomeTaxYearReportYear.q3 is not None):
#             q3.incomeBeforeIncomeTax = incomeBeforeIncomeTaxYearReportYear.q3.incomeBeforeIncomeTax
#
#         if (q4 is not None) and (incomeBeforeIncomeTaxYearReportYear.q4 is not None):
#             q4.incomeBeforeIncomeTax = incomeBeforeIncomeTaxYearReportYear.q4.incomeBeforeIncomeTax
#
#
#     if year in incomeBeforeIncomeTaxAndEquityInterestYearReport:
#         incomeBeforeIncomeTaxAndEquityInterestYear = incomeBeforeIncomeTaxAndEquityInterestYearReport[year]


# Sort the result
# sorted_operatingIncomeLossYearReport = get_sorted_year_report(operatingIncomeLossYearReport)
# sorted_incomeTaxExpenseBenefitYearReport = get_sorted_year_report(incomeTaxExpenseBenefitYearReport)
# sorted_incomeBeforeIncomeTaxYearReport = get_sorted_year_report(incomeBeforeIncomeTaxYearReport)
# sorted_incomeBeforeIncomeTaxAndEquityInterestYearReport = get_sorted_year_report(
#     incomeBeforeIncomeTaxAndEquityInterestYearReport)
#
# for index, report in enumerate(sorted_operatingIncomeLossYearReport):


# res_list = []
# for key in incomeTaxExpenseBenefitYearReport.keys():
#     res_list.append(incomeTaxExpenseBenefitYearReport[key])
# res_list.sort(key=lambda x: x.year, reverse=True)

# for year_report in res_list:
#     print(year_report)

# print(res)

# for data in operatingIncomeLossList:
#         print(data)

# print(operatingIncomeLossList)
# print(incomeTaxExpenseBenefitList)

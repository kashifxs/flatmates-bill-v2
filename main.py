import enum
import webbrowser
from datetime import date
from functools import reduce
from typing import List
from fpdf import FPDF

from datetime import datetime, timedelta


class Duration:
    """
    Class to represent a staying duration of a flatmate during a quarter of year,
    duration is calculated by difference of checkout date and checkin date.
    If checkout date is not provided it takes the last date of the quarter.
    """

    def __init__(self, check_in_date: str, check_out_date: str = ""):
        try:
            self.checkin = None
            self.checkin = date.fromisoformat(check_in_date)
            self.checkout = None
            if len(check_out_date) != 0:
                self.checkout = date.fromisoformat(check_out_date)
            else:
                self.checkout = self.get_last_date_of_quarter()
        except Exception as e:
            print(str(e))
            exit(0)

    def calculate_number_of_days(self):
        return self.checkout - self.checkin

    def get_last_date_of_quarter(self):
        checkin = self.checkin
        month = checkin.month
        y = str(checkin.year)
        if month > -1 and month <= 3:
            m = "03"
            d = "31"
        elif month >= 4 and month <= 6:
            m = "06"
            d = "30"
        elif month >= 7 and month <= 9:
            m = "09"
            d = "30"
        else:
            m = "12"
            d = "31"
        date_str = y + "-" + m + "-" + d
        return date.fromisoformat(date_str)


class Flatmates:
    """
    Class to hold values of each flatmate's name and list of checkin, checkout dates during a quarter of year.
     It calculates the  bill amount to pay
    based on the total number of days the flatmate had stayed.
    for calculating , flatmate needs a bill and
    """
    total_flatmates = 0
    total_days = 0

    def __init__(self, name: str, duration: List[Duration]):
        self.name = name
        self.durations = duration
        self.total_days_of_flatmate=0
        for d in self.durations:
            self.total_days_of_flatmate = self.total_days_of_flatmate + d.calculate_number_of_days().days
        Flatmates.total_days = Flatmates.total_days + self.total_days_of_flatmate

    def pay(self, bill: 'Bill'):
        fixed_costs = bill.get_total_fixed_costs()
        variable_costs = bill.get_total_variable_costs()
        fixed_amount = fixed_costs / Flatmates.total_flatmates
        variable_amount = round(variable_costs * self.total_days_of_flatmate / Flatmates.total_days,2)
        return round(fixed_amount + variable_amount,2)

    @staticmethod
    def display(flatmates: List['Flatmates'],bill:'Bill'):
        for flatmate in flatmates:
            print("{fl_name}\t{dy}\t{amount}\n".format(fl_name=flatmate.name, amount=flatmate.pay(bill),
                                                       dy=flatmate.total_days_of_flatmate))


class CostType(enum.Enum):
    """
    Class to represent different type of costs
    """
    Fixed = 1
    Variable = 2


class Cost:
    """
    Class to hold cost type and amount
    """

    def __init__(self, cost_name: str, cost_type: CostType, amount: float):
        self.cost_type = cost_type
        self.amount = amount
        self.cost_name = cost_name

    @staticmethod
    def is_fixed(cost: 'Cost'):
        return cost.cost_type == "F"

    @staticmethod
    def is_Variable(cost: 'Cost'):
        return cost.cost_type == "V"


class Bill:
    """
    Class to represent the Bill for a quarter of a year, A bill consist of various fixed or variable costs
    """
    bill_year = 2020
    bill_quarter = 1

    def __init__(self, costs: List[Cost]):
        self.costs = costs

    def get_total_fixed_costs(self):
        fixed_costs = filter(Cost.is_fixed, self.costs)
        total=0
        for cost in fixed_costs:
            total =total +cost.amount
        return total

    def get_total_variable_costs(self):
        variable_costs = filter(Cost.is_Variable, self.costs)
        total=0
        for cost in variable_costs:
            total =total +cost.amount
        return total


class PDFDocument:
    @staticmethod
    def generate(flatmates: List['Flatmates'],bill:'Bill'):
        pdf = FPDF(orientation='p', unit='pt', format="A4")
        pdf.add_page()
        pdf.image("house.png",w=30,h=30)
        pdf.set_font(family="Times", size=24, style="B")
        pdf.cell(w=0, border=0, h=80, txt="Flatmates Bill", align="C", ln=1)
        pdf.set_font(family="Times", size=16, style="B")
        pdf.cell(w=120, h=40, border=0, align="C", txt="Period:")
        pdf.cell(w=120, h=40, border=0, align="C", txt=str(Bill.bill_year) + " (Quarter " + str(Bill.bill_quarter) + ")", ln=1)
        pdf.cell(w=120, h=40, border=0, align="C", txt="Fixed Costs:", ln=1)
        pdf.set_font(family="Times", size=11)
        for cost in bill.costs:
            if cost.cost_type=="F":
                pdf.cell(w=120, h=40, border=0, align="C", txt=str(cost.cost_name.capitalize()))
                pdf.cell(w=240, h=40, border=0, align="C", txt=str(cost.amount),ln=1)
        pdf.set_font(family="Times", size=16, style="B")
        pdf.cell(w=120, h=40, border=0, align="C", txt="Variable Costs:", ln=1)
        pdf.set_font(family="Times", size=11)
        for cost in bill.costs:
            if cost.cost_type=="V":
                pdf.cell(w=120, h=40, border=0, align="C", txt=str(cost.cost_name.capitalize()))
                pdf.cell(w=240, h=40, border=0, align="C", txt=str(cost.amount),ln=1)
        pdf.set_font(family="Times", size=15,style="B")
        pdf.cell(w=120, h=40, border=0, align="C", txt="Total")
        pdf.cell(w=120, h=40, border=0, align="C", txt=str( bill.get_total_fixed_costs() + bill.get_total_variable_costs()), ln=1)
        pdf.cell(w=0, h=40, border=0, align="C", txt="",ln=1)
        pdf.set_font(family="Times", size=12, style="B")
        pdf.cell(w=0, h=40, border=0, align="C", txt="Flatmates share:",ln=1)
        pdf.cell(w=140, h=40, border=0, align="C", txt="Name")
        pdf.cell(w=120, h=40, border=0, align="C", txt="Duration")
        pdf.cell(w=80, h=40, border=0, align="C", txt="Amount", ln=1)
        pdf.set_font(family="Times", size=11)
        for fm in flatmates:
            pdf.cell(w=140, h=40, border=0, align="C", txt=fm.name.capitalize())
            pdf.cell(w=120, h=40, border=0, align="C", txt= str(fm.total_days_of_flatmate))
            pdf.cell(w=80, h=40, border=0, align="C", txt=str(fm.pay(bill)), ln=1)
        filename="bill_"+str(Bill.bill_year)+"_Q-"+str(Bill.bill_quarter)+".pdf"
        pdf.output(filename)
        webbrowser.open(filename)



# c1 = input("Enter checkin date in format yyyy-mm-dd")
# c2 = input("Enter check out date in yyyy-mm-dd format, enter blank for none")
#
#
# print("Duration:", d.calculate_number_of_days())
cost_names = []
costs = []
try:
    while True:
        bill_year = int(input("Enter bill year: "))
        if bill_year > date.today().year or bill_year < 2020:
            print(" Invalid year, please enter a year less than current year and greater than 2020 ")
            continue
        break
    while True:
        bill_quarter = int(input("For which quarter (1-4) ? "))
        if bill_quarter < 1 or bill_quarter > 4:
            print("Invalid quarter, Please enter quarter between 1-4")
            continue
        break
    Bill.bill_quarter=bill_quarter
    while True:

        while True:
            cost_name = input("Enter  bill cost name: ")
            if cost_name in cost_names:
                print("This item is already entered, please enter any other cost name")
                continue
            print("#####")
            cost_names.append(cost_name)
            break
        while True:
            cost_type = input("Is {costname} Fixed (f) or Variable(v):".format(costname=cost_name))
            if cost_type.lower() != "v" and cost_type.lower() != "f":
                print("Invalid value enter f for Fixed or v for variable")
                continue
            cost_type = cost_type.upper()
            break
        while True:
            amount = float(input("Enter amount for {costname}:".format(costname=cost_name)))
            if amount < 0 or amount > 5000:
                print("Invalid enter amount in range of 1-5000")
                continue
            break
        cost = Cost(cost_name, cost_type, amount)
        costs.append(cost)

        more_costs = input("Are there any more costs enter Y for yes, any other key for no: ")
        if more_costs.upper() != "Y":
            break

    flat_bill = Bill(costs)

    while True:
        num_flatmates = int(input("How many flatmates are sharing? "))
        if num_flatmates > 0 and num_flatmates < 5:
            break
        print("Invalid value, please enter a numeric value between 1 to 5")

    Flatmates.total_flatmates = num_flatmates
    flatmates_list = []
    for x in range(1, int(num_flatmates) + 1):
        name = input("Enter name for flatmate#: " + str(x) + ": ")
        durations = []
        while (True):
            checkin = input("Enter checkin date for {nm} in format yyyy-mm-dd: ".format(nm=name))
            checkout = input(
                "Enter check out date for {nm} in format yyyy-mm-dd: or enter blank if {nm} stayed throughout the period ".format(
                    nm=name))
            durations.append(Duration(checkin, checkout))
            if (len(checkout) == 0):
                break
            else:
                proceed = input("Is there is anymore checkin date for {nm}? (Y/N )".format(nm=name))
                if proceed == "n" or proceed == "N":
                    break
        flatmates_list.append(Flatmates(name, durations))
    Flatmates.display(flatmates_list,flat_bill)
    PDFDocument.generate(flatmates=flatmates_list,bill=flat_bill)
except Exception as e:
    throw(e)
    print(str(e))

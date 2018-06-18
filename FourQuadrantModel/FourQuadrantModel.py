import csv
import matplotlib.pyplot as plt
import numpy as np


def invertAxis(plot, axis):
    if axis == "x":
        values = plot.get_xlim()
        plot.set_xlim(values[1], values[0])
    if axis == "y":
        values = plot.get_ylim()
        plot.set_ylim(values[1], values[0])


def runRegression(indepVar, depVar):
    regressionCoeffs = np.polyfit(indepVar, depVar, 1)
    m = regressionCoeffs[0]
    b = regressionCoeffs[1]
    regressionData = [m*x+b for x in indepVar]
    return regressionData


def createPlot(plotArea, indepVar, depVar, title):
    plotArea.scatter(indepVar, depVar)
    plotArea.plot(indepVar, runRegression(indepVar, depVar))
    plotArea.set_title(title)
    return plotArea


def getColumn(rows, index):
    dataSeries = [r[index] for r in rows]
    return dataSeries


def interpretData(data):
    quantityVacant = getColumn(data, 0)
    rents = getColumn(data, 1)
    mktValues = getColumn(data, 2)
    constructionCosts = getColumn(data, 3)
    constructionQuantities = getColumn(data, 4)
    constructionTotals = getColumn(data, 5)
    percentRentals = getColumn(data, 6)

    # adjust propert values to account for construction constructionCosts
    # this will determine the equilibrium amount of construction
    adjustedPropValues = runRegression(mktValues, constructionCosts)

    # calculate equilibriam amount of construction
    # for a given property market value
    estConstruction = runRegression(adjustedPropValues, constructionTotals)

    # scale estimated construction porportionally
    # to actual construction rentals/total
    estConstruction = [a*b for a, b in zip(estConstruction, percentRentals)]

    # create graphs
    NEQuadrant = plt.subplot(222)
    createPlot(NEQuadrant, quantityVacant, rents,
               'Rental Space Market')
    NEQuadrant.set_xlabel('Quantity')
    NEQuadrant.set_ylabel('Rent')

    NWQuadrant = plt.subplot(221)
    createPlot(NWQuadrant, mktValues, rents,
               'Asset Market Valuation')
    invertAxis(NWQuadrant, 'x')
    NWQuadrant.set_ylabel('Rent')
    NWQuadrant.set_xlabel('Property Value')

    SWQuadrant = plt.subplot(223)
    createPlot(SWQuadrant, mktValues, estConstruction,
               'Construction Market')
    invertAxis(SWQuadrant, 'x')
    invertAxis(SWQuadrant, 'y')
    SWQuadrant.set_xlabel('Property Value')
    SWQuadrant.set_ylabel('Construction')

    SEQuadrant = plt.subplot(224)
    createPlot(SEQuadrant, quantityVacant, constructionQuantities,
               'Rental Stock Adjustment')
    invertAxis(SEQuadrant, 'y')
    SEQuadrant.set_xlabel('Quantity')
    SEQuadrant.set_ylabel('Construction')
    plt.show()


# transforms the data into the values needed for analysis
def transformDataRow(values, expectedExcessReturn):
    values = [float(v) for v in values[1:]]  # skipping first column (dates)
    vacantUnits = values[0]
    occupiedUnits = values[1]
    revenue = values[2]
    constructionsSpending = values[3]
    totalRentalConstruction = values[4] + values[5]
    totalConstruction = values[6] + values[7]
    capRate = values[8]/100+expectedExcessReturn
    rent = revenue/occupiedUnits
    propertyValue = rent/capRate
    constructionCostPerUnit = constructionsSpending/totalConstruction
    percentMultiFam = totalRentalConstruction/totalConstruction
    return[vacantUnits, rent, propertyValue,
           constructionCostPerUnit, totalRentalConstruction,
           totalConstruction, percentMultiFam]


# reads the csv dataFilename
# calls transformData method to normalize data for analysis and interpretation
def read_csv(file_handle, expectedExcessReturn):
    csvreader = csv.reader(file_handle)
    next(csvreader)  # skipping header
    transformedData = []
    for row in csvreader:
        transformedRow = transformDataRow(row, expectedExcessReturn)
        transformedData.append(transformedRow)
    interpretData(transformedData)


# program entry point
# first arg is the datafile
# second (optional) arg is excess return demandend by the investor
# and is added to the 10year treasury yield as proxy to the cap rate
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('dataFilename')
    ap.add_argument('--expectedExcessReturn', '-e', type=float, default=0.05)
    args = ap.parse_args()

    with open(args.dataFilename, 'r') as f:
        read_csv(f, args.expectedExcessReturn)

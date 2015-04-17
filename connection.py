#!/usr/bin/python

import sys
import datetime
import _mysql

# Main
def main():

  print("[STOCKS]")
  print(get_stocks("TSE", "T", datetime.datetime(2014, 01, 01), datetime.datetime(2014, 12, 31), "", "", ""))

  print("REGIONS]")
  print(get_regions())

  print("[COUNTRIES]")
  print(get_countries(""))
 
  print("[SECTORS]")  
  print(get_sectors())

# Get Stock Data
def get_stocks(exchange, symbol, start, end, region, country, sector):
  
  query = "SELECT Company.companyID, Exchange.exchangeCode, Company.Symbol, "
  query += "Date.year, Date.month, Date.day, Stock.close FROM Company "
  query += "INNER JOIN Country ON Company.countryID = Country.countryID "
  query += "INNER JOIN Region ON Region.regionID = Country.regionID "
  query += "INNER JOIN Sector ON Sector.sectorID = Company.sectorID "
  query += "INNER JOIN Exchange ON Exchange.exchangeID = Company.exchangeID "
  query += "INNER JOIN Stock ON Stock.companyID = Company.companyID "
  query += "INNER JOIN Date ON Date.dateID = Stock.dateID "
  query += " WHERE " 
  
  # Symbol 
  if symbol != "":
    query += "Company.symbol = '" + symbol + "' AND ";

  # Country
  if country != "": 
    query += "Country.country = '" + country + "' AND ";

  # Region
  if region != "":
    query += " Region.region = '" + region + "' AND ";

  # Sector
  if sector != "": 
    query += " Sector.sector = '" + sector + "' AND ";
  
# Exchange
  if exchange != "":
    query += " Exchange.exchangeCode = '" + exchange + "' AND ";

  # Date
  d1 = str(start.year) + str(start.month).zfill(2) + str(start.day).zfill(2)
  d2 = str(end.year) + str(end.month).zfill(2) + str(end.day).zfill(2)
  query += "CONCAT(Date.year, LPAD(Date.month, 2, '0'), LPAD(Date.day, 2, '0')) BETWEEN "
  query += d1 + " AND " + d2
  
  # End Query
  query += ";"
  
  # Query Database
  try:

    # Connection
    connection = _mysql.connect('99.254.1.29', 'rpeace', '3Q5CmaE7', 'Stocks')

    # Query
    connection.query(query)

    # Result
    result = connection.use_result()

    # Rows
    rows = result.fetch_row(result.num_rows())

  # Query Failed
  except _mysql.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

  # Close Connection
  finally:
    if connection:
      connection.close()

  return rows

# Get Regions
def get_regions():

  query = "SELECT region FROM Region;"

  # Query Database
  try:

    # Connection
    connection = _mysql.connect('99.254.1.29', 'rpeace', '3Q5CmaE7', 'Stocks')

    # Query
    connection.query(query)

    # Result
    result = connection.use_result()

    # Rows
    rows = result.fetch_row(result.num_rows())

  # Query Failed
  except _mysql.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

  # Close Connection
  finally:
    if connection:
      connection.close()

  return [ seq[0] for seq in rows ]

# Get Countries
def get_countries(region):

  query = "SELECT country FROM Country INNER JOIN Region ON Country.regionID = Region.regionID"

  # Region
  if region != "":
    query += " WHERE Region.region = '" + region + "'"

  # End Query
  query += ";"

  # Query Database
  try:

    # Connection
    connection = _mysql.connect('99.254.1.29', 'rpeace', '3Q5CmaE7', 'Stocks')

    # Query
    connection.query(query)

    # Result
    result = connection.use_result()

    # Rows
    rows = result.fetch_row(result.num_rows())

  # Query Failed
  except _mysql.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

  # Close Connection
  finally:
    if connection:
      connection.close()

  return [ seq[0] for seq in rows ]

# Get Sectors
def get_sectors():

  query = "SELECT sector FROM Sector;"

  # Query Database
  try:

    # Connection
    connection = _mysql.connect('99.254.1.29', 'rpeace', '3Q5CmaE7', 'Stocks')

    # Query
    connection.query(query)

    # Result
    result = connection.use_result()

    # Rows
    rows = result.fetch_row(result.num_rows())

  # Query Failed
  except _mysql.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

  # Close Connection
  finally:
    if connection:
      connection.close()

  return [ seq[0] for seq in rows ]


















# Execute Main
if __name__ == "__main__":
	main()

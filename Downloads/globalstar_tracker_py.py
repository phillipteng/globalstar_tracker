import cartopy
import cartopy.crs as ccrs
import numpy as np
import pylab as plt
import ephem
import datetime
import os
from ephem import degree
from datetime import datetime as date_t
import wget
import time



def loadTLE(filename):
    """ Loads a TLE file and creates a list of satellites."""
    f = open(filename)
    satlist = []
    l1 = f.readline()
    while l1:
        l2 = f.readline()
        l3 = f.readline()
        sat = ephem.readtle(l1,l2,l3)
        satlist.append(sat)
        print (sat.name)
        l1 = f.readline()
    
    f.close()
    print (len(satlist), "satellites loaded into list")
    return satlist

def main():
    # Define observer coordinates

    # Location of Wachusett Mountain
    # loc_lat = 42.503
    # loc_long = -71.886

    # Location of Haystack Observatory
    loc_lat = 42.623049
    loc_long = -71.488314
    observer = ephem.Observer()
    observer.lat = np.deg2rad(loc_lat)
    observer.long = np.deg2rad(loc_long)
    #moved observer.date = date_t.now() into the while loop

    if os.path.exists("globalstar.txt"):
        os.remove("globalstar.txt")
    else:
        print "The globalstar TLE does not exist"

    file = wget.download('http://celestrak.com/NORAD/elements/globalstar.txt') #get the updated file
	
    # Load TLE data
    globalstar = loadTLE("globalstar.txt")

    while True:
        #This is where I moved that line to so that it updates the time
        observer.date = date_t.now()

        # Define time interval (now until next 10 minutes)
        dt = [date_t.now() + datetime.timedelta(minutes = x) for x in range(0, 10)]
        sat_alt, sat_az = [], []
        sat_lat, sat_long = [], []
    
        for i in range(len(globalstar)):
            sat_alt.append([])
            sat_az.append([])
            sat_lat.append([])
            sat_long.append([])
    
            for date in dt:
                satellite = globalstar[i]
                satellite.compute(date)
                sat_lat[i].append(satellite.sublat / degree)
                sat_long[i].append(satellite.sublong / degree)
    
                observer.date = date
                satellite.compute(observer)
                sat_alt[i].append(np.rad2deg(satellite.alt))
                sat_az[i].append(np.rad2deg(satellite.az))
        
        plt.clf()
        plt.suptitle("Haystack Observatory: {}".format(date_t.now()), size=18)
        ax = plt.subplot(121, projection = ccrs.PlateCarree())
        ax.add_feature(cartopy.feature.OCEAN)
        ax.add_feature(cartopy.feature.LAND)
        ax.add_feature(cartopy.feature.COASTLINE)
        ax.add_feature(cartopy.feature.BORDERS, linestyle = '-')
    
        ax.set_extent([-135, -20, -10, 80], crs=ccrs.PlateCarree())
    
        # Plot our reference location
        plt.plot(loc_long, loc_lat,
                 color = 'red',
                 marker = '*',
                 transform = ccrs.Geodetic()
                 )
    
        # Plot satellites on map
        for i in range(len(globalstar)):
            plt.scatter(sat_long[i][0],	sat_lat[i][0],
                        linewidth = 4,
                        transform = ccrs.Geodetic()
                        )
    
            ax.annotate(globalstar[i].name[11:15], (sat_long[i][0] -3 ,sat_lat[i][0] - 3))
    
            plt.plot(sat_long[i], sat_lat[i],
                     linewidth = 2,
                     transform = ccrs.Geodetic()
                     )
            plt.plot(sat_long[i][-1], sat_lat[i][-1],
                     linewidth = 2,
                     color = 'black',
                     marker = 'x',
                     transform = ccrs.Geodetic()
                     )
    	
        # Plot satellites on polar az/el graph
        ax = plt.subplot(122, polar=True)
        for i in range(len(globalstar)):
            ax.scatter(np.deg2rad(sat_az[i][0]), 
                       90 - np.array(sat_alt[i][0]),
                       linewidth = '3')
            ax.annotate(globalstar[i].name[11:15], (np.deg2rad(sat_az[i][0]),90 - np.array(sat_alt[i][0])))
            ax.plot(np.deg2rad(sat_az[i]), 90 - np.array(sat_alt[i]))
            ax.plot(np.deg2rad(sat_az[i][-1]), 
                    90 - np.array(sat_alt[i][-1]),
                    linewidth = '2',
                    color = 'black',
                    marker = 'x'
                    )
    
        ax.set_ylim(0,90)
        ax.set_theta_direction(-1)
        ax.set_theta_offset(np.pi / 2)
        #ax.yaxis.set_ticklabels([])
        ax.grid(True)
        plt.ion() # turn on interactive mode
        plt.show() # show the plot
        plt.pause(2) # pause for two seconds before updating
	
if __name__ == '__main__':
    main()
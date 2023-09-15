import numpy as np

def PredictBNThickness(RGBcontr) -> float:
    # RGBcontr: RGB contrast, a 3-element array, defined as (flake - background) / background
    RGBcontr = np.array(RGBcontr)
    RGBcontr = np.reshape(RGBcontr, (3,1))
    database = '3200'
    if database == 'auto':
        coeff = -np.array([[0,-0.0308184170107591,0.00139144292948507,-9.26117147614618e-06],
                           [0,-0.0104456490648191,0.00159911620332250,-2.00630707746733e-05],
                           [0,0.0322533172243514,-0.000115785060275143,-4.54973076334403e-06]])
        RGBstd = np.reshape(np.array([0.0502, 0.0727, 0.0357]), (3,1))
    else:
        coeff = -np.array([[0,-0.0285213886560541,0.00113487265867389,1.30375956820257e-05,-3.75758446030200e-07],
                           [0,-0.0230025091896823,0.00388373682332100,-0.000103536651398996,8.59135973055619e-07],
                           [0,0.0475961781129818,-0.000891471249500990,9.15197908551476e-06,-4.58931561297204e-08]])
        RGBstd = np.reshape(np.array([0.0142, 0.0172, 0.0225]), (3,1))
    z = np.linspace(0,50,501)
    predcontr = np.zeros([3,np.size(z)])
    for i in range(3):
        polyval = z*0
        coeffi = coeff[i]
        for j in range(len(coeffi)):
            polyval += coeffi[j]*(z**j)
        predcontr[i] = polyval
    err = np.sum((predcontr - RGBcontr)**2/RGBstd**2,axis=0)
    predz = z[np.argmin(err)]
    try:
        lowerbound = min(z[err < min(err)*2])
        upperbound = max(z[err < min(err)*2])
    except:
        lowerbound, upperbound = 0, 0
    err = (upperbound - lowerbound) / 2
    return predz, err


if __name__ == '__main__':
    out = PredictBNThickness([0.1661,0.7196,1.0485])
    out = PredictBNThickness([0, 0, 0.1])


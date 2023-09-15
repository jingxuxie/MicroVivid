#%%
import numpy as np
import matplotlib.pyplot as plt

def predictThickness(RGBcontr) -> float:
    # RGBcontr: RGB contrast, a 3-element array, defined as (flake - background) / background
    RGBcontr = np.array(RGBcontr)
    RGBcontr = np.reshape(RGBcontr, (3,1))
    database = '3200'
    if database == 'auto':
        coeff = [[0,-0.0308184170107591,0.00139144292948507,-9.26117147614618e-06],
                [0,-0.0104456490648191,0.00159911620332250,-2.00630707746733e-05],
                [0,0.0322533172243514,-0.000115785060275143,-4.54973076334403e-06]]
        db = np.loadtxt('RGBZauto.txt')
        RGBstd = np.reshape(np.array([0.0502, 0.0727, 0.0357]), (3,1))
    else:
        coeff = [[0,-0.0285213886560541,0.00113487265867389,1.30375956820257e-05,-3.75758446030200e-07],
                [0,-0.0230025091896823,0.00388373682332100,-0.000103536651398996,8.59135973055619e-07],
                [0,0.0475961781129818,-0.000891471249500990,9.15197908551476e-06,-4.58931561297204e-08]]
        db = np.loadtxt('RGBZ3200.txt')
        RGBstd = np.reshape(np.array([0.0142, 0.0172, 0.0225]), (3,1))
    z = np.linspace(0,50,501)
    color = ['r','g','b']
    predcontr = np.zeros([3,np.size(z)])
    fg = plt.figure()
    ax = fg.add_subplot(111)
    ax2 = ax.twinx()
    for i in range(3):
        polyval = z*0
        coeffi = coeff[i]
        for j in range(len(coeffi)):
            polyval += coeffi[j]*(z**j)
        predcontr[i] = polyval
        ax.plot(z,polyval,color[i])
        ax.scatter(db[:,3],db[:,i],4,color=color[i])
    err = np.sum((predcontr - RGBcontr)**2/RGBstd**2,axis=0)
    predz = z[np.argmin(err)]
    lowerbound = min(z[err < min(err)*2])
    upperbound = max(z[err < min(err)*2])
    for i in range(3):
        ax.scatter(predz,RGBcontr[i],color=color[i],marker='+')
    ax2.axvline(x=predz, color="black", linestyle="--", linewidth=0.5)
    ax2.plot(z,err,color=[0.6,0.6,0.6])
    ax2.set_yscale('log')
    ax.set_title('Predicted thickness: '+f"{predz:.1f}"+r' $\pm$ '+f"{upperbound/2-lowerbound/2:.1f}"+' nm')
    plt.show()
    return predz


predictThickness([0.1661,0.7196,1.0485])
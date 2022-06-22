#!/usr/bin/env python
# coding: utf-8

# In[17]:


get_ipython().run_line_magic('matplotlib', 'notebook')
latslider = IntSlider(value=0, min=-90, max=90, step=1, description='Lat:')
doy  = np.array([i for i in range(1, 366)])
sza  = np.array([get_solar_zenith(latslider.value, i) for i in range(1, 366)])

fig  = plt.figure(num=0, figsize=(8, 3))
ln,  = plt.plot(doy, sza, label=None)
plt.xlim(doy[0], doy[-1]); plt.ylim(-90, 90)  # set x,y limits
plt.ylabel("zenith angle [deg]")              # add ylabel 
plt.xlabel("day of the year")                 # add xlabel 

def pupdate(lat):
    """Update plot."""
    sza = np.array([get_solar_zenith(lat, i) for i in range(1, 366)])
    ln.set_ydata(sza)
  
interact(pupdate, lat=latslider)

def black(par1, par2, par3, sza):
    """Calculate black sky albedo for MCD43A1 band parameters."""
    
    iso = ( 1.000000,  0.000000, 0.000000)          # iso: Isotropic
    vol = (-0.007574, -0.070987, 0.307588)          # vol: RossThick
    geo = (-1.284909, -0.166314, 0.041840)          # geo: LiSparseR
    
    s = np.radians(sza)                             # get sza in radians
    sza2, sza3 = s**2, s**3                         # get exponentiated sza
    func = lambda p1, p2, p3: (                     # def apply function
        p1*(iso[0]+iso[1]*sza2+iso[2]*sza3)+        #  iso
        p2*(vol[0]+vol[1]*sza2+vol[2]*sza3)+        #  vol
        p3*(geo[0]+geo[1]*sza2+geo[2]*sza3))        #  geo
    
    return(xr.apply_ufunc(func, par1, par2, par3))

def white(par1, par2, par3):
    """ """
    func = lambda p1, p2, p3: (
        p1* 1.000000 +                             # Isotropic
        p2* 0.189184 +                             # RossThick
        p3*-1.377622 )                             # LiSparseR 
    return(xr.apply_ufunc(func, par1, par2, par3))


get_ipython().run_line_magic('matplotlib', 'notebook')

def blue(wsa, bsa, lookup):
    """Vectorize albedo polynomials over two 3d arrays."""
    func = lambda white,black,lookup: (white*lookup) + (black*(1 - lookup))
    return(xr.apply_ufunc(func, wsa, bsa, lookup))

def lookup(band, sza, sod=0.20):
    """Look up blue albedo skyl_lut value."""    
    od = '%.2f' % sod
    luc = band.lookup[od]
    lfunc = lambda s: luc.iloc[s]
    return(xr.apply_ufunc(lfunc, abs(sza).round()))

def get_ylim(bsa,wsa,alb):
    a = np.array([bsa,wsa, alb])
    return(np.nanmin(a), np.nanmax(a))


# albedos --------------------------------------------------------------------

bsa = black(p1, p2, p3, sza)
wsa = white(p1, p2, p3)
lu  = lookup(px[band_name], sza).values.reshape(sza.shape)
alb = blue(bsa, wsa, lu)

# plot -----------------------------------------------------------------------

fig = plt.figure(num=3, figsize=(8,3))
lalb, = plt.plot(px.time, alb, label="blue")
lbsa, = plt.plot(px.time, bsa, label="black", color="black")
lwsa, = plt.plot(px.time, wsa, label="white", color="gray")

plt.xlim(px.time[0].data, px.time[-1].data)     # set x limits
plt.ylim(get_ylim(bsa,wsa,alb))                 # set y limits
plt.legend(loc="upper right", borderpad=0.75)   # add legend
plt.ylabel("albedo [unitless]")                 # add ylabel 
plt.title("BLACK, WHITE, BLUE SKY ALBEDOS")

# widgets and events ---------------------------------------------------------

def update_ylim(change):
    plt.ylim(get_ylim(bsa,wsa,alb))

def update(BAND, SZA, SOD):
    band = px[BAND]
    
    p1, p2, p3 = [band.sel(param=n).squeeze() for n in [0,1,2]]
    bsa = black(p1, p2, p3, SZA)
    wsa = white(p1, p2, p3)
    
    sza = np.array([SZA]*365)
    lu  = lookup(band, sza, SOD).values.reshape(sza.shape)
    alb = blue(bsa, wsa, lu)
    
    lbsa.set_ydata(bsa)
    lwsa.set_ydata(wsa)
    lalb.set_ydata(alb)
    
    plt.ylim(min([bsa.min().item(), wsa.min().item(), alb.min().item()]),
             max([bsa.max().item(), wsa.max().item(), alb.max().item()]))

lyt   = Layout(width="40%")
wsza  = FloatSlider(min=0, max=90, step=0.00001, value=45.0, layout=lyt)
wod   = FloatSlider(min=0.02, max=0.98, step=0.02, value=0.20, layout=lyt) 
wband = Dropdown(options=bands, value=bands[0], layout=lyt)
wband.observe(update_ylim, names='value')

interact(update, BAND=wband, SZA=wsza, SOD=wod);


# In[ ]:





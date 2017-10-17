# RAKON TCXO E6245LF Phase Noise Profile, Taken from the datasheet for CMOS Output, 30.72 MHz
fpn_ref_e6245lf=[1.0e2, 1.0e3, 1.0e4, 1.0e5]
pn_ref_e6245lf=[-128.0, -148.0, -152.0, -156.0]
noise_floor_ref_e6245lf=-159

# RAKON TCXO E6245LF Phase Noise Profile, Taken from the datasheet for Clipped-Sine Output, 40.0 MHz
fpn_ref_rtx5032a=[1.0e2, 1.0e3, 1.0e4, 1.0e5]
pn_ref_rtx5032a=[-110.0, -138.0, -151.0, -154.0]
noise_floor_ref_rtx5032a=-156.0

# Feedback Divider Phase Noise @ Output- No Supply Noise Included, With Bond Inductance in VDD and GND
fpn_fbdiv_sim_noLDO=[1.0e3, 1.0e4, 1.0e5, 1.0e6]
pn_fbdiv_sim_noLDO=[-143.5, -154.2, -164.0, -164.0]
noise_floor_fbdiv_sim_noLDO=-164.0 # corrected from -170 to -164, june 07. 2016.

# Feedback Divider Phase Noise @ Output- With MIC37122 Supply Noise Included, With Bond Inductance in VDD and GND
fpn_fbdiv_sim_mic37122=[1.0e3, 3.0e3, 1.0e4, 4.0e4, 1.0e5, 3.33e5, 9.0e5]
pn_fbdiv_sim_mic37122=[-140.9, -142.9, -143.95, -143.72, -142.8, -144.25, -155.17]
noise_floor_fbdiv_sim_mic37122=-156.9

# Feedback Divider Phase Noise @ Output- With ADM7155 Supply Noise Included, With Bond Inductance in VDD and GND
fpn_fbdiv_sim_adm7155=[1.0e3, 1.0e4, 1.0e5]
pn_fbdiv_sim_adm7155=[-143.5, -154.2, -163.5]
noise_floor_fbdiv_sim_adm7155=-168

# VCO-FFDIV-LODIST Path Phase Noise @ LODIST Output - No Supply Noise Included, With Bond Inductance in VDD and GND
# VCO Only
fc_vco_sim_noLDO=200.0e3
fpn_vco_sim_noLDO=[1.0e3, 1.0e4, 1.0e5, 1.0e6, 1.0e7]
pn_vco_sim_noLDO=[-38.6, -74.5, -103.11, -125.7, -148.3]
noise_floor_vco_sim_noLDO=-150.0


# VCO-FFDIV-LODIST Path Phase Noise @ LODIST Output - With MIC37122 Supply Noise Included, With Bond Inductance in VDD and GND
fc_vco_sim_mic37122=200.0e3
#fpn_vco_sim_mic37122=[1.0e3, 1.0e4, 1.0e5, 5.7e5, 1.0e6, 1.0e7]
fpn_vco_sim_mic37122=[1.0e3, 1.0e4, 2.0e4, 4.0e4, 1.0e5, 2.0e5, 1.0e6]
#pn_vco_sim_mic37122=[-38.6, -72.8, -94.4, -112.2, -125.7, -141.11]
pn_vco_sim_mic37122=[-41.0, -70.2, -78.0, -83.0, -93.6, -109, -122.0]
noise_floor_vco_sim_mic37122=-150.0

# VCO-FFDIV-LODIST Path Phase Noise @ LODIST Output - With ADM7155 Supply Noise Included, With Bond Inductance in VDD and GND
fc_vco_sim_adm7155=200.0e3
fpn_vco_sim_adm7155=[1.0e3, 1.0e4, 1.0e5, 1.0e6, 1.0e7]
pn_vco_sim_adm7155=[-38.6, -74.5, -103.11, -125.4, -142.0]
noise_floor_vco_sim_adm7155=-150.0

# VCO-FFDIV-LODIST Measured Phase Noise, AMP=1
fc_vco_meas_amp1=200.0e3
fpn_vco_meas_amp1=[1.0e3, 1.0e4, 2.0e4, 4.0e4, 1.0e5, 2.0e5, 1.0e6]
pn_vco_meas_amp1=[-40.5, -69.0, -76.8, -79.1, -90.3, -105, -122.0]
noise_floor_vco_meas_amp1=-150.0

# VCO-FFDIV-LODIST Measured Phase Noise, AMP=3
fc_vco_meas_amp3=200.0e3
fpn_vco_meas_amp3=[1.0e3, 1.0e4, 2.0e4, 4.0e4, 1.0e5, 2.0e5, 1.0e6]
pn_vco_meas_amp3=[-41.0, -70.2, -78.0, -83.0, -93.6, -109, -122.0]
noise_floor_vco_meas_amp3=-150.0

# XBUF Phase Noise @ Output- No Supply Noise Included, With Bond Inductance in VDD and GND
fpn_xbuf_sim_noLDO=[1.0e3, 1.0e4, 1.0e5, 1.0e6]
pn_xbuf_sim_noLDO=[-153.9, -161.9, -164.9, -164.9]
noise_floor_xbuf_sim_noLDO=-165.4

# XBUF Phase Noise @ Output- With MIC37122 Supply Noise Included, With Bond Inductance in VDD and GND
fpn_xbuf_sim_mic37122=[1.0e3, 1.0e4, 1.0e5, 5.6e5, 1.0e6, 6.0e6]
pn_xbuf_sim_mic37122=[-142.5, -142.7, -141.45, -144.0, -150.8, -153.2]
noise_floor_xbuf_sim_mic37122=-154.0

# XBUF Phase Noise @ Output- With ADM7155 Supply Noise Included, With Bond Inductance in VDD and GND
fpn_xbuf_sim_adm7155=[1.0e3, 1.0e4, 1.0e5]
pn_xbuf_sim_adm7155=[-153.5, -160.5, -162.6]
noise_floor_xbuf_sim_adm7155=-164.0

# CP Simulated Output Noise Current, pA/sqrt(Hz), no LDO Noise, With Bond Inductance in VDD and GND
fn_cp_sim_noLDO=[1.0e3, 1.0e4, 1.0e5, 1.0e6, 10.0e6, 100.0e6]
In_cp_sim_noLDO=[5.1e-12, 2.8e-12, 2.4e-12, 2.4e-12, 2.4e-12, 2.4e-12]

# CP Simulated Output Noise Current, pA/sqrt(Hz), MIC37122 Noise, With Bond Inductance in VDD and GND
fn_cp_sim_mic37122=[1.0e3, 1.0e4, 1.0e5, 1.0e6, 10.0e6, 100.0e6]
In_cp_sim_mic37122=[6.3e-12, 4.6e-12, 4.42e-12, 4.42e-12, 4.42e-12, 4.42e-12]

# CP Simulated Output Noise Current, pA/sqrt(Hz), ADM7155 Noise, With Bond Inductance in VDD and GND
fn_cp_sim_adm7155=[1.0e3, 1.0e4, 1.0e5, 1.0e6, 10.0e6, 100.0e6]
In_cp_sim_adm7155=[5.13e-12, 2.85e-12, 2.51e-12, 2.48e-12, 2.48e-12, 2.48e-12]

# CP white current noise spectrum in A/sqrt(Hz), added as an overhead to the calculated values
# It can be used to accomodate the values calculated in the Python model to the simulation results
# Can include the effects of noise folding due to SD Quantization Noise, LDO Noise etc.
In_cp_white_sim_noLDO=2.4e-12
In_cp_white_sim_mic37122=4.4e-12
In_cp_white_sim_adm7155=2.46e-12




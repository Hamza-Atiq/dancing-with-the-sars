"""Decode GUNW uint32 mask using the downloaded product's own description."""
import numpy as np

def gunw_quality(mask):
    m=np.asarray(mask,dtype=np.uint32)
    low=m & 255
    ref=(low//10)%10
    sec=low%10
    water=low//100
    anomalies=(m>>8)&65535
    valid=(low!=255)&(ref>=1)&(ref<=5)&(sec>=1)&(sec<=5)&(water==0)&(anomalies==0)&((m>>25)==0)
    return {'valid_land':valid,'ionosphere_interpolated':((m>>24)&1).astype(bool),
            'reference_subswath':ref,'secondary_subswath':sec,'anomaly_bits':anomalies}

def goff_valid_land(mask):
    # GOFF reserves bits 24-31; unlike GUNW, it has no ionosphere flag.
    m=np.asarray(mask,dtype=np.uint32)
    return gunw_quality(m)['valid_land'] & ((m>>24)==0)

if __name__=='__main__':
    # Actual observed codes plus boundary/anomaly cases.
    values=np.array([0,1,10,11,12,111,255,16777228,267,65547],dtype=np.uint32)
    expected=[False,False,False,True,True,False,False,True,False,False]
    assert gunw_quality(values)['valid_land'].tolist()==expected
    assert gunw_quality(values)['ionosphere_interpolated'].tolist()==[False]*7+[True,False,False]
    assert goff_valid_land(values).tolist()==[False,False,False,True,True,False,False,False,False,False]
    print('GUNW and GOFF mask decoding checks passed')

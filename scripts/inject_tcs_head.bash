#!/bin/bash
# inject_tcs_head.bash
# KW Lin 2026 Jun 14
#
# This script gets the status from the TCS and prints it out
# Since it calls "tcs_talk" this must be run in the observer environment

echo "STATUS" | tcs_talk | python3 -c "
import sys
import os
import subprocess
data = sys.stdin.buffer.read()
print('total bytes received: %d' % len(data))
if len(data) >= 60:
    ra_raw  = data[3:12].decode(errors='replace').strip()
    dec_raw = data[13:22].decode(errors='replace').strip()
    ha      = data[24:33].decode(errors='replace').strip()
    lst     = data[34:42].decode(errors='replace').strip()
    alt     = data[43:48].decode(errors='replace').strip()
    azim    = data[49:55].decode(errors='replace').strip()
    
    # Convert RA to decimal hrs and Dec to decimal deg
    # this is the format printed on grafana and in obsplans
    ra_hh   = float(ra_raw[0:2])
    ra_mm   = float(ra_raw[2:4])
    ra_ss   = float(ra_raw[4:])
    ra_dec  = ra_hh + ra_mm/60.0 + ra_ss/3600.00
    
    sign    = -1.0 if dec_raw[0] == '-' else 1.0
    dec_dd  = float(dec_raw[1:3])
    dec_mm  = float(dec_raw[3:5])
    dec_ss  = float(dec_raw[5:])
    dec_deg = sign * (dec_dd + dec_mm/60.0 + dec_ss/3600.0)
    
    print('RA   : [%s] = %.6f hours' % (ra_raw, ra_dec))
    print('DEC  : [%s] = %.6f degrees' % (dec_raw, dec_deg))
    print('HA   : [%s]' % ha)
    print('LST  : [%s]' % lst)
    print('ALT  : [%s]' % alt)
    print('AZ   : [%s]' % azim)

    # Send header keywords to the CCP
    host = os.environ.get('CCP_HOST', 'ls4-workstn')
    port = os.environ.get('CCP_PORT', '6000')
    keywords = [
        ('TELE-RA', '%.6f' % ra_dec),
        ('TELE-DEC', '%.6f' % dec_deg),
        ('HA', ha),
        ('LST', lst),
        ('TEL_RA', '%.6f' % ra_dec),
        ('TEL_DEC', '%.6f' % dec_deg),
        ('TEL_HA', ha),
        ('TEL_LST', lst),
        ('TEL_ALT', alt),
        ('TEL_AZ', azim),
    ]
    for kw, val in keywords:
        cmd = 'echo \"header %s %s\" | netcat -N %s %s' % (kw, val, host, port)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print('%s %s -> %s' % (kw, val, result.stdout.strip()))
"

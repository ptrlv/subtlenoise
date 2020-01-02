# Welcome to Sonic Pi v3.1

use_osc "localhost",4559
use_osc_logging false
use_cue_logging false
use_synth_defaults amp: 1.0

#Duration of jobs is mapped to frequency of note. Midi note to be played given by dj-mqtt.py
#Want to increase amplitude of low notes, decrease for high notes to balance the spectrum.

sample :mehackit_robot1

live_loop :message do
  use_real_time
  n = sync "/osc/message"
  puts n
  use_synth :hollow
  duration = 2 + Math.log10([n[1], 1].max)
  freq = n[0]
  
  play hz_to_midi(freq), attack: 0, decay: 0.05, release: duration, amp: 0.3, pan: n[2]
end
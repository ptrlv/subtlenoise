# Welcome to Sonic Pi v3.1

use_osc "localhost",4559
use_osc_logging false
use_cue_logging false
use_synth_defaults amp: 1.0

#Duration of jobs is mapped to frequency of note. Midi note to be played given by dj-mqtt.py
#Want to increase amplitude of low notes, decrease for high notes to balance the spectrum.

sample :mehackit_robot1

live_loop :badness do
  use_real_time
  n = sync "/osc/badness"
  puts n
  use_synth :prophet
  play 39, attack: 0, decay: 0.05, release: 1.0, res: 0.9, amp: 0.5
end

live_loop :goodness do
  use_real_time
  n = sync "/osc/goodness"
  puts n
  duration = 2 + Math.log10([n[1], 1].max)
  #duration = 5.0
  ampFactor = 0.0 + 20.0/n[0] #Increases volume of lower notes
  
  midi = n[0]
  #print midi
  use_synth :hollow
  play midi, attack: 0, decay: 0.05, release: duration, res: 0.8, amp: ampFactor, cutoff: 110, pan: n[2]
end
use_osc "localhost",4559
use_osc_logging false
use_cue_logging false
use_synth_defaults amp: 1.0

sample :mehackit_robot1

live_loop :test do
  use_real_time
  use_synth :gnoise
  n = sync "/osc/test"
  puts n
  #duration = Math.log10(n[0])
  #use_synth :blade
  #play :e3, pulse_width: 0.95, release: duration, sub_amp: 4, amp: 1
  use_synth :pulse
  play 90, attack: 0, sustain: 0, decay: 0.5, release: 0.1, res: 0.9
  #use_synth :hollow
  #play 30, attack: 0, decay: 1, release: duration, res: 0.9, amp: 0.2
end

live_loop :ping do
  use_real_time
  use_synth :gnoise
  n = sync "/osc/ping"
  puts n
  #  use_synth :blade
  #  play :e3, release: 0.02, amp: 1
  use_synth :pulse
  play 80, attack: 0, sustain: 0, decay: 0.03, release: 0.05, res: 0.95, cutoff: 80
end

live_loop :badness do
  use_real_time
  n = sync "/osc/badness"
  puts n
  use_synth :prophet
  #play 30, attack: 0, sustain: 1, decay: 0.1, release: 0.1, res: 0.91, width: 2, sustain_level: 0.1
  play 30, attack: 0, decay: 0.05, release: 1.0, res: 0.9, amp: 0.2
end

live_loop :goodness do
  use_real_time
  n = sync "/osc/goodness"
  puts n
  #sample :misc_cineboom
  duration = Math.log10([n[0], 1].max)
  #duration = [duration, 1].min
  print duration
  use_synth :hollow
  play 50, attack: 0, decay: 0.05, release: duration, res: 0.9, amp: 0.5
  #play 30, attack: 0, sustain: 1, decay: 0.1, release: 0.1, res: 0.91, width: 2, sustain_level: 0.1
end

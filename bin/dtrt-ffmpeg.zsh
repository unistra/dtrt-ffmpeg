setopt nounset warncreateglobal extendedglob braceccl

use_slurm=${use_slurm:-false} use_cuvid=${use_cuvid:-false}
output_template='${input:t:r}_${width}x${height}.${input:e}'

encoder=( ffmpeg  -v error -nostats )
available_sizes=(
    320.240
    720.480
    1280.720
    1920.1080 )

workdir=.

# outch ... doesn't work with old versions of zsh :(
# alias @='for it'
# alias @-='while {read it}'

# TODO: XDG support ?
for it ( ~/.dtrt-ffpmeg(N) ) . $it

video_info_get () { ffprobe \
    -v error -select_streams v \
    -show_entries stream=${2?list of infos to print separated by a coma} \
    -of default=noprint_wrappers=1:nokey=1 ${1?path of the video} }


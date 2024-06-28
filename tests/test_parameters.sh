# Test script for the python script 'parameters.py' that is called externally:
# One variable is set to missing so that it can be checked how the script
# behaves in that case

PWDDIR=$(pwd)
export java_memory="some_java_memory"
export processes="some_processes"
export hts="some_hts"
export sampling_rate="some_sampling_rate"
export random_seed="some_random_seed"
#export output_id="some_output_id"
python3 "$PWDDIR/parameters.py" "$PWDDIR/tests/fixtures/testfile.yml" "$PWDDIR/tests/fixtures/testoutput.yml"

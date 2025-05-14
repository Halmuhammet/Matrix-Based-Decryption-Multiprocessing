#!/bin/bash
#SBATCH --job-name=FullGrader
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j
#SBATCH --partition=quanah
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=36
#SBATCH --time=48:00:00
#SBATCH --mem-per-cpu=5370MB  #5.3GB per core
#SBATCH --mail-type=ALL
#SBATCH --mail-user=hmuhamed@ttu.edu

declare -a inArr=("/lustre/work/errees/courses/cs3361/final_project/input_files/short.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/short.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/short.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/short.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/short.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/short.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/medium.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/medium.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/medium.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/medium.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/medium.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/medium.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/long.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/long.txt"
				  "/lustre/work/errees/courses/cs3361/final_project/input_files/long.txt"
				  )

declare -a md5Arr=("/lustre/work/errees/courses/cs3361/final_project/output_files/short.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/short.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/short.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/short.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/short.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/short.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/medium.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/medium.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/medium.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/medium.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/medium.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/medium.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/long.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/long.md5"
				   "/lustre/work/errees/courses/cs3361/final_project/output_files/long.md5"
				   )

declare -a outArr=("full_short"
				   "full_short"
				   "full_short"
				   "full_short"
				   "full_short"
				   "full_short"
				   "full_medium"
				   "full_medium"
				   "full_medium"
				   "full_medium"
				   "full_medium"
				   "full_medium"
				   "full_long"
				   "full_long"
				   "full_long"
				   )

declare -a procArr=("1"
					"2"
					"4"
					"8"
					"16"
					"32"
					"1"
					"2"
					"4"
					"8"
					"16"
					"32"
					"9"
					"18"
					"36"
					)
					
declare -a seedArr=("baccabacca"
					"baccabacca"
					"baccabacca"
					"baccabacca"
					"baccabacca"
					"baccabacca"
					"cabacbca"
					"cabacbca"
					"cabacbca"
					"cabacbca"
					"cabacbca"
					"cabacbca"
					"abc"
					"abc"
					"abc"
					)

#Override field separators to line terminators and store the original field separators.
OIFS="$IFS"
IFS=$'\n'

# Set up modules and load the CS3361 conda environment.
module purge
module load intel
. /lustre/work/errees/courses/cs3361/final_project/conda/etc/profile.d/conda.sh 	
conda activate

# Set some necessary variables for pattern matching and looping
pattern="[[:alnum:]]+_[[:alnum:]]+_R[[:digit:]]+_final_project\.py"
arrLength=${#inArr[@]}
directory=$(pwd)

# Create the timing and correctness files.
echo -e "Test Run Results:" > full_correctness.log
echo -e "Run Time Results:" > full_timing.log

# Loop through the files in the directory
for file in "$directory"/*; do
    if [[ $file =~ $pattern ]]; then
		
		#Run all test cases and print their correctness and runtime.
		for ((i=0; i<$arrLength; i++))
		do
			#Assume incorrect, verify correctness.
			correctness="Incorrect"
			
			# Set the output file name
			outFile="${outArr[$i]}_${procArr[$i]}.out"
			
			# Clean up previous output file (Protection in the event a script tries to append)
			rm -f $outFile
			
			# Run the script and calculate runtime.
			startTime=`date +%s.%N`
			python3 $file -i ${inArr[$i]} -o $outFile -s ${seedArr[$i]} -p ${procArr[$i]} &> full_output.out
			endTime=`date +%s.%N`
			runTime=`echo $endTime - $startTime | bc`
			
			#Determine Correctness
			outputHash=$(tr -d '[:space:]' < "$outFile" | md5sum | awk '{print $1}')
			expectedHash=$(cat "${md5Arr[$i]}" | awk '{print $1}')
			
			if [ "$outputHash" = "$expectedHash" ]; then
				correctness="Correct"
			fi
			
			# Write correctness and timing data to log files:
			if [ ${procArr[$i]} = "1" ]; then
				printf "%-40s" "    ${outArr[$i]} - ${procArr[$i]} process:" >> full_correctness.log
				printf "%-40s" "    ${outArr[$i]} - ${procArr[$i]} process:" >> full_timing.log
			else
				printf "%-40s" "    ${outArr[$i]} - ${procArr[$i]} processes:" >> full_correctness.log
				printf "%-40s" "    ${outArr[$i]} - ${procArr[$i]} processes:" >> full_timing.log
			fi
			printf "$correctness\n" >> full_correctness.log
			printf "$runTime seconds\n" >> full_timing.log
		done
    fi
done

#Return the field separator to its original value and deactivate conda.
IFS="$OIFS"
conda deactivate
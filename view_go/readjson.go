package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"strings"
)

type Maintenance struct {
	Nodes     []string `json:"nodes"`
	StartTime int64    `json:"start_time"`
	EndTime   int64    `json:"end_time"`
}

type Node struct {
	Name     string `json:"name"`
	NGpus    int    `json:"n_gpus"`
	GpuModel string `json:"gpu_model"`
	Reserved bool   `json:"reserved"` // string in new version
	Status   string `json:"status"`
	Cpus     int    `json:"cpus"`
	Mem      int    `json:"mem"`
}

type Infrastructure struct {
	Maintenances   []Maintenance `json:"maintenances"`
	Nodes          []Node        `json:"nodes"`
	GpuLimitPu     int           `json:"gpu_limit_pu"`
	GpuLimitGrp    int           `json:"gpu_limit_grp"`
	GpuLimitStu    int           `json:"gpu_limit_stu"`
	GpuLimitStuGrp int           `json:"gpu_limit_stugrp"`
	RamLimitPu     int           `json:"ram_limit_pu"`
	RamLimitGrp    int           `json:"ram_limit_grp"`
	RamLimitStu    int           `json:"ram_limit_stu"`
	RamLimitStuGrp int           `json:"ram_limit_stugrp"`
	Prior          []string      `json:"prior"`
}

type Joblet struct {
	JobId     string `json:"jobid"`
	TrueJobId string `json:"true_jobid"`
	Node      string `json:"node"`
	NGpus     int    `json:"n_gpus"`
	Mem       int    `json:"mem"`
	Cpus      int    `json:"cpus"`
}

type Job struct {
	JobId     string   `json:"jobid"`
	TrueJobId string   `json:"true_jobid"`
	Name      string   `json:"name"`
	User      string   `json:"user"`
	Partition string   `json:"partition"`
	State     string   `json:"state"`
	Runtime   string   `json:"runtime"`
	Joblets   []Joblet `json:"joblets"`
	Reason    string   `json:"reason"`
}

type Dump struct {
	Infrastructure Infrastructure `json:"infrastructure"`
	Jobs           []Job          `json:"jobs"`
}

func (d Dump) GetJoblets() ([]Joblet, []Job) {
	var joblets []Joblet
	var jobs []Job
	for _, job := range d.Jobs {
		for _, joblet := range job.Joblets {
			joblets = append(joblets, joblet)
			jobs = append(jobs, job)
		}
	}
	return joblets, jobs
}

func GetDump(filename string) Dump {
	// Open our jsonFile
	jsonFile, err := os.Open(filename)
	// if we os.Open returns an error then handle it
	if err != nil {
		fmt.Println(err)
	}
	// defer the closing of our jsonFile so that we can parse it later on
	defer jsonFile.Close()

	// read our opened jsonFile as a byte array.
	byteValue, _ := ioutil.ReadAll(jsonFile)
	byteString := string(byteValue[:])
	byteString = strings.Replace(byteString, "NaN", "null", -1)
	byteString = strings.Replace(byteString, ".0,", ",", -1)

	byteValue = []byte(byteString)

	// we initialize our Dump array
	var dump Dump

	// we unmarshal our byteArray which contains our
	// jsonFile's content into 'users' which we defined above
	err = json.Unmarshal(byteValue, &dump)

	// if there is an error, handle it
	if err != nil {
		fmt.Println(err)
	}

	return dump
}

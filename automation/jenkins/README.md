* [Active Jobs](#active-jobs)
* [Builds](#builds)
* [Computers By Arch OS Version](#computers-by-arch-os-version)
* [Computers By Label](#computers-by-label)
* [Jenkins Slave Java versions](#jenkins-slave-java-versions)
* [Jenkins Master projects](#jenkins-master-projects)

# Active Jobs

    List all active jobs on the Jenkins Master host, and what their previous build status was.
    
    ./active_jobs.py -H <Jenkins Master host name> -p <Jenkins Master port>

# Builds

    List information about each of the last x days worth of builds.
    Depending upon how many days are specified, this could take a long time.
    
    ./builds -H <Jenkins Master host name> -p <Jenkins Master port>
             -d <days back to search> -s "<string to search for>"
             -j <limit search to specific project/job> -b <limit search to specific build number>

# Computers By Arch OS Version

    Show computers known by the Jenkins Master sorted by architecture, OS, and OS version
    
    ./computers_by_arch_os_version.py -H <Jenkins Master host name> -p <Jenkins Master port>

# Computers By Label

    Show computers known by the Jenkins Master sorted by the label(s) in which they appear
    
    ./computers_by_label.py -H <Jenkins Master host name> -p <Jenkins Master port>

# Jenkins Slave Java versions

    Show Java version of each Slave known to the Jenkins Master
    
    ./java_versions.py -H <Jenkins Master host name> -p <Jenkins Master port>

# Jenkins Master projects

    Show all projects/jobs configured on the Jenkins Master
    
    ./projects.py -H <Jenkins Master host name> -p <Jenkins Master port>

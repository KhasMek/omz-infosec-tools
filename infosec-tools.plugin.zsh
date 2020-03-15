# Boop

__INFOSEC_TOOLS_DIR="${0:A:h}"

# https://www.publicsuffix.org/list/public_suffix_list.dat
export TLDEXTRACT_CACHE="${__INFOSEC_TOOLS_DIR}/res/data/public_suffix_list.dat"

function gen_subdomain() {
    python3 "${__INFOSEC_TOOLS_DIR}/gen_subdomain.py" $@
}

function ip_calc() {
    python3 "${__INFOSEC_TOOLS_DIR}/ip_calc.py" $@
}

function nmap_gen_port_targets() {
    python3 "${__INFOSEC_TOOLS_DIR}/nmap_gen_port_targets.py" $@
}

function pyserv_simple_http() {
    python -m SimpleHTTPServer
}

function update_service_port_dictionary() {
    print "  Downloading port service data for port_search.py"
    if [ ! -d "${__INFOSEC_TOOLS_DIR}/res/data" ]; then
        echo "  Creating ${__INFOSEC_TOOLS_DIR}/res/data"
    	echo "mkdir -p ${__INFOSEC_TOOLS_DIR}/res/data"
    fi
    wget https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv -q -O "${__INFOSEC_TOOLS_DIR}/res/data/service-names-port-numbers.csv"
    print "  Download Complete!"
}
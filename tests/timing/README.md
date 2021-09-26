# API get performance

# Accessing relevant Kibana logs: https://kibana.polaris.pn.telstra.com:5601/app/discover#/view/a42c2660-d1a4-11ea-a069-211cc36e779a?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-4h,to:now))&_a=(columns:!(original_path,timestamp,upstream_svc_time,duration,authority),filters:!(('$state':(store:appState),meta:(alias:!n,disabled:!f,index:'logstash-*',key:type,negate:!t,params:(query:ms-java-apimanager),type:phrase),query:(match_phrase:(type:ms-java-apimanager)))),index:'logstash-*',interval:auto,query:(language:kuery,query:'%22%2Feis%2F1.0.0%2Fendpoint%2Fendpointuuid%22%20'),sort:!())

## no concurrency

time tpn endpoints list
real    1m35.806s
user    0m1.988s
sys     0m0.246s

## concurrent.futures

time tpn endpoints list
real    0m14.117s
user    0m0.721s
sys     0m0.174s

time tpn endpoints list
real    0m15.090s
user    0m0.744s
sys     0m0.181s

VAGRANTFILE_API_VERSION = "2"

ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'
ENV['VAGRANT_NO_PARALLEL'] = "1"
ENV['FORWARD_DOCKER_PORTS'] = "1"
ENV['VAGRANT_EXPERIMENTAL'] ="typed_triggers"

unless Vagrant.has_plugin?("vagrant-docker-compose")
    system("vagrant plugin install vagrant-docker-compose")
    puts "Dependencies installed, please try the command again."
    exit
end

TREE_DEPTH_LEVEL = 3
CLIENTS_COUNT = (2**TREE_DEPTH_LEVEL) - 1

ZOONODE_IMAGE = "ds/task03/silhavyj/zoonode:0.1"
CLIENT_IMAGE  = "ds/task03/silhavyj/client:0.1"
UTILS_IMAGE   = "ds/task03/silhavyj/utils:0.1"

CLIENTS = { 
    :nameprefix => "client-",
    :subnet => "176.0.1.",
    :ip_offset => 100,
    :image => CLIENT_IMAGE 
}

ROOT_NODE_IDX      = 0
ROOT_NAME          = "#{CLIENTS[:nameprefix]}#{ROOT_NODE_IDX}"
ROOT_IP_ADDR       = "#{CLIENTS[:subnet]}#{CLIENTS[:ip_offset] + ROOT_NODE_IDX}"
ZOONODE_IP_ADDR    = "#{CLIENTS[:subnet]}#{CLIENTS[:ip_offset] - 1}"
UTILS_NODE_IP_ADDR = "#{CLIENTS[:subnet]}#{CLIENTS[:ip_offset] - 2}"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.trigger.before :up, type: :command do |trigger|
        trigger.name = "Build docker images"
        trigger.ruby do |env, machine|
            puts "Building utils image:"
            `docker build utils -t "#{UTILS_IMAGE}"`

            puts "Building node image:"
            `docker build client -t "#{CLIENT_IMAGE}"`

            puts "Building zoonode image:"
            `docker build zoonode -t "#{ZOONODE_IMAGE}"`
        end
    end

    config.ssh.insert_key = false

    config.vm.define "node-utils" do |utils|
        utils.vm.network "private_network", ip: UTILS_NODE_IP_ADDR
        utils.vm.hostname = "zoonode"
        utils.vm.network "forwarded_port", guest: 80, host: 5000, host_ip: "0.0.0.0", auto_correct: true
        utils.vm.provider "docker" do |d|
            d.image = UTILS_IMAGE
            d.name = "node-utils"
            d.has_ssh = true
            d.env = {
                "ZOO_SERVERS" => ZOONODE_IP_ADDR
            }
        end
        utils.vm.post_up_message = "Node 'zoonode' up and running. You can access the node with 'vagrant ssh zoonode'}"
    end

    config.vm.define "zoonode" do |s|
        s.vm.network "private_network", ip: ZOONODE_IP_ADDR
        s.vm.hostname = "zoonode"
        s.vm.network "forwarded_port", guest: 80, host: 5000, host_ip: "0.0.0.0", auto_correct: true
        s.vm.provider "docker" do |d|
            d.image = ZOONODE_IMAGE
            d.name = "zoonode"
            d.has_ssh = true
        end
        s.vm.post_up_message = "Node 'zoonode' up and running. You can access the node with 'vagrant ssh zoonode'}"
    end

    config.vm.define ROOT_NAME do |root|
        root.vm.network "private_network", ip: ROOT_IP_ADDR
        root.vm.network "forwarded_port", guest: 80, host: 5000, host_ip: "0.0.0.0", auto_correct: true
        root.vm.hostname = ROOT_NAME
        root.vm.provider "docker" do |d|
            d.image = CLIENTS[:image]
            d.name = ROOT_NAME
            d.has_ssh = true
            d.env = {
                "ROOT_NODE" => "#{ROOT_IP_ADDR}",
                "NODE_ADDRESS" => "#{ROOT_IP_ADDR}",
                "ZOO_SERVERS" => ZOONODE_IP_ADDR,
                "CLIENT_COUNT" => "#{CLIENTS_COUNT}",
            }
        end
    end

    (0..CLIENTS_COUNT - 1).each do |i|
        if i != ROOT_NODE_IDX
            node_ip_addr = "#{CLIENTS[:subnet]}#{CLIENTS[:ip_offset] + i}"
            node_name = "#{CLIENTS[:nameprefix]}#{i}"
            config.vm.define node_name do |s|
                s.vm.network "private_network", ip: node_ip_addr
                s.vm.network "forwarded_port", guest: 80, host: 5000, host_ip: "0.0.0.0", auto_correct: true
                s.vm.hostname = "#{CLIENTS[:nameprefix]}#{i}"
                s.vm.provider "docker" do |d|
                    d.image = CLIENTS[:image]
                    d.name = node_name
                    d.has_ssh = true
                    d.env = {
                        "ROOT_NODE" => ROOT_IP_ADDR,
                        "NODE_ADDRESS" => node_ip_addr,
                        "ZOO_SERVERS" => ZOONODE_IP_ADDR
                    }
                end
                s.vm.post_up_message = "Node #{node_name} up and running. You can access the node with 'docker exec -it #{node_name} bash'}"
            end
        end
    end
end

# EOF
<html>

	<head>
        <title>Valkyrie</title>
        <meta http-equiv="refresh" content="300" />
	</head>
	
    <body>

    <h1>Farm Status</h1>

    <%
    import datetime
    displaytime = datetime.datetime.strptime(utctime, '%Y-%m-%d %H:%M:%S.%f').strftime('%H:%M UTC on %b %d')
    %>

    <h2>Overall Status at ${displaytime}</h2>

    <p>
        Hashrate: ${total_hashrate} <br/>
        Active Miners: ${total_miners} <br/>
        Active GPUs: ${total_gpus} <br/>
        Temperature: ${temperature}
    </p>

    <h2>Devices</h2>

    <table border="1">
        <tr>
            <th>Miner</th>
            <th>Device</th>
            <th>Status</th>
            <th>Hashrate (KH/s)</th>
            <th>Temperature</th>
            <th>Fan %</th>
            <th>Intensity</th>
            <th>GPU Act.</th>
            <th>GPU Clock</th>
            <th>Mem Clock</th>
            <th>Powertune</th>
            <th>GPU Volt.</th>
            <th>HW Errors</th>
            <th>Rej %</th>
        </tr>
    % for minername in miners:
        %for dev in miners[minername]['devs']:
            <% dev_hashrate = dev['MHS 5s'] * 1000 %>
        <tr>
            <td>${minername}</td>
            <td>Dev ${dev['GPU']}</td>
            <td>${dev['Status']}</td>
            <td>${dev_hashrate}</td>
            <td>${dev['Temperature']}</td>
            <td>${dev['Fan Percent']}</td>
            <td>${dev['Intensity']}</td>
            <td>${dev['GPU Activity']}</td>
            <td>${dev['GPU Clock']}</td>
            <td>${dev['Memory Clock']}</td>
            <td>${dev['Powertune']}</td>
            <td>${dev['GPU Voltage']}</td>
            <td>${dev['Hardware Errors']}</td>
            <td>${dev['Device Rejected%']}</td>
        </tr>
        %endfor
    % endfor
    </table>

    <h2>Miners</h2>

    <table border="1">
        <tr>
            <th>Miner</th>
            <th>Hashrate</th>
            <th>Avg. Hashrate</th>
            <th>Accepted</th>
            <th>Rejected %</th>
        </tr>
    % for minername in miners:
        <% summary = miners[minername]['summary'] %>
        <tr>
            <td>${minername}</td>
            <td>${summary['MHS 5s']}</td>
            <td>${summary['MHS av']}</td>
            <td>${summary['Accepted']}</td>
            <td>${summary['Device Rejected%']}</td>
        </tr>

    % endfor
    </table>

    <h2>Pools</h2>

    <table border="1">
        <tr>
            <th>Miner</th>
            <th>URL</th>
            <th>User</th>
            <th>Active</th>
            <th>Status</th>
            <th>Priority</th>
            <th>Accepted</th>
            <th>Rej %</th>
        </tr>
    % for minername in miners:
        %for pool in miners[minername]['pools']:
        <tr>
            <td>${minername}</td>
            <td>${pool['URL']}</td>
            <td>${pool['User']}</td>
            <td>${pool['Stratum Active']}</td>
            <td>${pool['Status']}</td>
            <td>${pool['Priority']}</td>
            <td>${pool['Accepted']}</td>
            <td>${pool['Pool Rejected%']}</td>
        </tr>
        %endfor
    % endfor
    </table>

    <h2>Configurations</h2>

    <table border="1">
        <tr>
            <th>Miner</th>
            <th>OS</th>
            <th>GPUs</th>
            <th>Strategy</th>
        </tr>
    % for minername in miners:
        %for config in miners[minername]['config']:
        <tr>
            <td>${minername}</td>
            <td>${config['OS']}</td>
            <td>${config['GPU Count']}</td>
            <td>${config['Strategy']}</td>
        </tr>
        %endfor
    % endfor
    </table>

    <p>This page refreshes every five minutes.</p>

    </body>
    
</html>
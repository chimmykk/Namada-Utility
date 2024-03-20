from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)
port = 3500

@app.route('/finalltxn', methods=['POST'])
def process_transaction():
    data = request.json
    receiver = data.get('receiver')
    amount = data.get('amount')
    
    try:
        # Add /usr/local/bin to the PATH environment variable
        os.environ['PATH'] += ':/usr/local/bin'
        
        result = subprocess.run(['hermes', 'tx', 'ft-transfer',
                                 '--src-chain', 'osmo-test-5',
                                 '--dst-chain', 'shielded-expedition.88f17d1d14',
                                 '--src-port', 'transfer',
                                 '--src-channel', 'channel-6448',
                                 '--key-name', 'osmosisrelay',
                                 '--receiver', receiver,
                                 '--amount', str(amount),
                                 '--denom', 'uosmo',
                                 '--timeout-seconds', '60',
                                 '--timeout-height-offset', '180'],
                               capture_output=True, text=True)
        
        print(result.returncode)
        print(result.stdout)
        print(result.stderr)
        
        if result.returncode != 0:
            return jsonify({'error': 'Internal server error'}), 500
        elif result.stderr:
            return jsonify({'error': 'Bad request'}), 400
        else:
            return jsonify({'message': 'Transaction executed successfully'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(port=port)

import React, { Component } from 'react';

let COMPILER_ENDPOINT = "https://mem-track-6c05e.appspot.com"

/* 
Test Input:

int total(int num){
int sum=0;
for(int i=0;i<num;i=i+1){
sum=sum+5;
}
return sum;
} 
*/

class App extends Component {

  constructor(props) {
    super(props);
    this.inputRef = React.createRef();
    this.state = {
      codeMem: [...Array(100).keys()].map(key => ({ memAddress: key + 1, value: "0000000000000000" })),
      compMem: [...Array(100).keys()].map(key => ({ memAddress: key + 101, value: "0000000000000000" })),
      compiledCode: [],
      compilingMessage: null
    }
  }

  compileAndSave() {
    // get text from textarea
    let inputCode = this.inputRef.current.value
    // convert every letter to ascii (base10)
    let asciiArray = inputCode.trim().split('').map(letter => letter.charCodeAt(0))
    // empty out the memory
    let newCodeMem = [...Array(100).keys()].map(key => ({ memAddress: key + 1, value: "0000000000000000" }))

    let counter = 0
    while (asciiArray.length > 0) {
      // get the first 2 ascii ints
      let next2 = asciiArray.splice(0, 2)
      // convert to binary and add missing "0"s
      let bin1 = next2[0].toString(2)
      bin1 = [...Array(8 - bin1.length).keys()].map(_ => "0").join("") + bin1
      let bin2 = next2.length === 2 ? next2[1].toString(2) : "00000000"
      bin2 = [...Array(8 - bin2.length).keys()].map(_ => "0").join("") + bin2
      // replace memory with binary representations of ascii chars
      newCodeMem[counter] = {
        memAddress: counter + 1,
        value: `${bin1}${bin2}`
      }
      counter++
    }
    // update the rendered data
    this.setState({ codeMem: newCodeMem, compilingMessage: "Compiling...", compiledCode: [] })
    fetch(`${COMPILER_ENDPOINT}/compile`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        codeInput: inputCode.split("\n").map(line => line.trim())
      })
    }).then(response => response.json()).then(json => {
      this.setState({ compilingMessage: null, compiledCode: json })
    }).catch(err => {
      this.setState({ compilingMessage: "Failed to compile." })
    })

  }

  render() {
    return (
      <div style={{ display: 'flex', flexWrap: 'wrap', height: '100vh', justifyContent: 'space-between' }}>
        <div style={{ flexDirection: 'column', display: 'flex', margin: 8, flexGrow: 1 }}>
          <h3>Enter Program Here:</h3>


          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <textarea ref={this.inputRef} style={{ minHeight: 300 }}></textarea>
            <input
              type="button"
              style={{ minHeight: 30 }}
              value="Submit"
              onClick={() => this.compileAndSave()}
            />
            {<p>{this.state.compilingMessage}</p>}
            <p>
              {this.state.compiledCode.map((line, key) => <span key={key}>{line}<br /></span>)}
            </p>
          </div>

        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', height: '100%', flexGrow: 1 }}>
          <div style={{ height: '100%', flex: 1 }}>
            <h3 style={{ margin: 8 }}>ASCII</h3>
            <div style={{ height: '100%', overflowY: 'scroll' }}>
              {this.state.codeMem.map(key => <p key={key.memAddress}>{key.memAddress} {key.value}</p>)}
            </div>
          </div>
          <div style={{ height: '100%', flex: 1 }}>
            <h3 style={{ margin: 8 }}>Assembly</h3>
            <div style={{ height: '100%', overflowY: 'scroll' }}>
              {this.state.compMem.map(key => <p key={key.memAddress}>{key.memAddress} {key.value}</p>)}
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default App;

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
      codeMem: [],
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
    let newCodeMem = []

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
      body: JSON.stringify(
        inputCode.split("\n").map(line => {
          let trimmed = line.trim()
          let output = ""
          for (let i = 0; i < trimmed.length; i++) {
            if (trimmed[i] !== " " || (trimmed.substring(i - 3, i) === "int") || (trimmed.substring(i - 6, i) === "return")) {
              output += trimmed[i]
            }
          }
          return output
        })
      )
    }).then(response => response.json()).then(json => {
      this.setState({ compilingMessage: "Compiled Successfuly", compiledCode: json })
    }).catch(err => {
      this.setState({ compilingMessage: "Failed to compile." })
    })

  }

  render() {
    return (
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-around' }}>
        <div style={{ flexDirection: 'column', display: 'flex', margin: 8, flexGrow: 1, maxWidth: 600 }}>
          <h3>Enter Program Here:</h3>


          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', width: '100%'}}>
            <textarea ref={this.inputRef} style={{ minHeight: 300 }}></textarea>
            <input
              type="button"
              style={{ minHeight: 30 }}
              value="Submit"
              onClick={() => this.compileAndSave()}
            />

          </div>

        </div>
        <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, maxWidth: 600}}>
            <div style={{ overflowY: 'scroll', display: 'flex', flexDirection: 'column' }}>
              {<p>{this.state.compilingMessage}</p>}
              <p>
                {this.state.compiledCode.map((line, key) => <span key={key}>{line}<br /></span>)}
              </p>
            </div>
        </div>
        {this.state.codeMem.length > 0 && <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, maxWidth: 600 }}>
            <h3 >ASCII Storage</h3>
            <div style={{ overflowY: 'scroll', display: 'flex', flexDirection: 'column', height: '90vh' }}>
              {this.state.codeMem.map(key => <p key={key.memAddress}>{key.memAddress} {key.value}</p>)}
            </div>
        </div>}
      </div>
    );
  }
}

export default App;

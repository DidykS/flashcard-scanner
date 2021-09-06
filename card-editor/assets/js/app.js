// start vue app
const App = {
  data() {
    return {
      title: "Card Editor",
      originalArr: [], // originalArr - original data
      copiedArr: [], // copiedArr - copied data from the original array
    }
  },
  mounted() {},
  methods: {
    // push to the original array
    async originalPush() {
      let file = document.querySelector("#file").files[0]
      let data

      data = await this.loadFile(file)
      // let test = JSON.parse(data)
      let test = JSON.parse(data)
      this.originalArr = test.cards

      // card verification
      this.originalArr.forEach((item) => {
        if (item.languages == undefined) {
          item.languages = {
            en: {
              topic: "Test",
              words: ["test", "test2"],
            },
            uk: {
              topic: "Test",
              words: ["test", "test2"],
            },
          }
        } else if (item.languages.en == undefined) {
          item.languages.en = {
            topic: "Test",
            words: ["test", "test2"],
          }
        } else if (item.languages.uk == undefined) {
          item.languages.uk = {
            topic: "Test",
            words: ["test", "test2"],
          }
        }
      })

      // copy originalArr
      this.copyOriginal()
    },
    // the method that loads a file
    loadFile(file) {
      return new Promise((resolve, reject) => {
        let reader = new FileReader()

        reader.onload = function (event) {
          let data = event.target.result
          resolve(data)
        }

        reader.readAsText(file)
      })
    },
    // copyOriginal method:
    copyOriginal() {
      this.copiedArr = JSON.parse(JSON.stringify(this.originalArr))
    },
    // change item id
    changeItemId(item, e) {
      item.id = Number(e.target.value)
      e.target.value = ""
    },
    // change item en topic
    changeItemEnTopic(item, e) {
      item.languages.en.topic = e.target.value
      e.target.value = ""
    },
    // change en words
    changeEnWords(item, e) {
      let target = e.target.value
      item.languages.en.words = target.split("/")
      e.target.value = ""
    },
    // change item uk topic
    changeItemUkTopic(item, e) {
      item.languages.uk.topic = e.target.value
      e.target.value = ""
    },
    // change en words
    changeUkWords(item, e) {
      let target = e.target.value
      item.languages.uk.words = target.split("/")
      e.target.value = ""
    },
    // download function
    download(fileName, content) {
      let element = document.createElement("a")
      element.style.display = "none"

      element.setAttribute(
        "href",
        "data:text/plain;charset=utf-8," + encodeURIComponent(content)
      )

      element.setAttribute("download", fileName)
      document.body.appendChild(element)
      element.click()
      document.body.removeChild(element)
    },
    // Here, when the user clicks the download button, start download
    downloadFile() {
      // let content = JSON.stringify(this.copied)
      let content = JSON.stringify(this.copiedArr)
      let fileName = "test.json"
      this.download(fileName, content)
    },
  },
}

Vue.createApp(App).mount("#container")

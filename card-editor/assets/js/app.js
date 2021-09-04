// start vue app
const App = {
  data() {
    return {
      title: "Card Editor",
      originalArr: [], // originalArr - original data
      copiedArr: [] // copiedArr - copied data from the original array
    }
  },
  mounted() {
  },
  methods: {
    // push to the original array
    async originalPush() {
      let file = document.querySelector("#file").files[0]
      let data

      data = await this.loadFile(file)
      this.originalArr.push(...JSON.parse(data))
      this.copyOriginal()
    },
    // the method that loads a file 
    loadFile(file) {
      return new Promise((resolve, reject) => {
        let reader = new FileReader()

        reader.onload = function(event) {
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
      item.languages.en.words = target.split(",")
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
      item.languages.uk.words = target.split(",")
      e.target.value = ""
    }
  }
}

Vue.createApp(App).mount("#container")

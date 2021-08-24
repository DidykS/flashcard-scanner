// impotr card JSON file from folder
import json from "../../B2-1.json" assert { type: "json" }

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
    this.pushOriginal()
    this.copyOriginal()
  },
  methods: {
    // pushOriginal method:
    pushOriginal() {
      this.originalArr.push(...json)
    },
    // copyOriginal method:
    copyOriginal() {
      this.copiedArr = JSON.parse(JSON.stringify(this.originalArr))
    }
  }
}

Vue.createApp(App).mount("#container")

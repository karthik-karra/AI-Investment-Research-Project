<template>
  <div class="chart-container">
    <apexchart type="area" height="350" :options="chartOptions" :series="series"></apexchart>
  </div>
</template>

<script>
import VueApexCharts from 'vue3-apexcharts';

export default {
  name: 'StockChart',
  components: {
    apexchart: VueApexCharts,
  },
  props: {
    // This prop will receive the data from App.vue
    chartData: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  computed: {
    // Computed property to format the data for the chart's series
    series() {
      return [{
        name: 'Stock Price',
        data: this.chartData
      }];
    },
    chartOptions() {
      return {
        chart: {
          height: 350,
          type: 'area',
          toolbar: { show: true }
        },
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth' },
        xaxis: {
          type: 'datetime',
          labels: {
            format: 'MMM yy'
          }
        },
        yaxis: {
          labels: {
            formatter: function (value) {
              return "$" + value.toFixed(2);
            }
          },
        },
        tooltip: {
          x: { format: 'dd MMM yyyy' },
        },
      };
    }
  }
}
</script>
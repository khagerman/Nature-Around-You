BASE_URL = "https://api.inaturalist.org/v1";

async function getSimilarSpecies() {
  const id = await axios.get("/similarspecies");
  natureId = id.data.nature_id;
  const res = await axios.get(
    `${BASE_URL}/identifications/similar_species?taxon_id=${natureId}`
  );

  for (result of res.data.results) {
    let newLivingThing = showSimilar(result);
    $("#hidden_similar").append(newLivingThing);
  }
  // $("#similar").off("click");
}

$("#similar").on("click", async function (e) {
  e.preventDefault();

  const $this = $(this);
  if ($this.hasClass("clicked-once")) {
    $("#hidden_similar").hide();
    $("#hidden_similar").empty();
    $("#similar").html(
      `View Similar Species <i class="fas fa-chevron-down"></i>`
    );
    $this.removeClass("clicked-once");
  } else {
    getSimilarSpecies();
    $("#hidden_similar").show();
    $("#similar").html(
      `View Similar Species <i class="fas fa-chevron-up"></i>`
    );
    $this.addClass("clicked-once");
  }
});

function showSimilar(result) {
  let photo = result.taxon.default_photo.medium_url;

  return `
  <div class="col m-3">
<div class="card rounded" style="width: 14rem;">
    <img class="card-img-top" src="${photo}" style="width: 14rem;">
    <div class="card-body">
        <h6 class="card-text text-center">${
          result.taxon.preferred_common_name
            ? result.taxon.preferred_common_name
            : result.taxon.name
        }</h6>
      
    </div>
    <a href="${result.taxon.id}" class="stretched-link">
    </a>
</div>
</div>

`;
}

// get classifications on click

async function getClassifications() {
  const res = await axios.get("/classifications");
  $(".loading").show();
  for (result of res.data.results) {
    // console.log(result[0].default_photo.medium_url);
    let classification = showClassifications(result);
    $("#classifications").append(classification);
    $(".loading").hide();
  }
}
$("#classifybutton").on("click", async function (e) {
  e.preventDefault();

  const $this = $(this);
  if ($this.hasClass("clicked-once")) {
    $("#classifications").hide();
    $("#classifications").empty();
    $("#classifybutton").html(
      `View Classfications <i class="fas fa-chevron-down"></i>`
    );
    $this.removeClass("clicked-once");
  } else {
    $("#classifications").show();
    $("#classifybutton").html(
      `View Classfications <i class="fas fa-chevron-up"></i>`
    );
    getClassifications();
    $this.addClass("clicked-once");
  }
});

function showClassifications(result) {
  return `
  <div class="col-3 m-3 ">
  <div class="card">
    <img class="card-img-top" src="${result[0].default_photo.medium_url}">
    <div class="card-body">
        <h6 class="card-text text-center">${
          result[0].preferred_common_name
            ? result[0].preferred_common_name
            : result[0].name
        }</h6>
      
    </div>
    <a href="${result[0].id}" class="stretched-link">
    </a>
</div>
</div>

`;
}

// $(body).on({
//   ajaxStart: function () {
//     $(".loading").show();
//   },
//   ajaxStop: function () {
//     $(".loading").hide();
//   },
// });

// bootstrap carosel and collapse code
$(".carousel").carousel();
$(".collapse").collapse();

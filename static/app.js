BASE_URL = "https://api.inaturalist.org/v1";

$("#similar").on("click", async function (e) {
  e.preventDefault();
  const $this = $(this);
  if ($this.hasClass("clicked-once")) {
    $("#hidden_similar").hide();
  } else {
    $("#hidden_similar").show();
    getSimilarSpecies();
    $this.addClass("clicked-once");
  }
});
async function getSimilarSpecies() {
  const id = await axios.get("/similarspecies");
  natureId = id.data.nature_id;
  const res = await axios.get(
    `${BASE_URL}/identifications/similar_species?taxon_id=${natureId}`
  );
  console.log(res);
  for (result of res.data.results) {
    let newLivingThing = showSimilar(result);
    $("#hidden_similar").append(newLivingThing);
  }
  $("#similar").off("click");
}

function showSimilar(result) {
  let photo = result.taxon.default_photo.medium_url;
  console.log(result.taxon.default_photo);
  return `
  <div class="col m-3">
<div class="card" style="width: 14rem;">
    <img class="card-img-top" src="${photo}" style="width: 14rem;">
    <div class="card-body">
        <h6 class="card-text">${
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
// bootstrap carosel and collapse code
$(".carousel").carousel();
$(".collapse").collapse();

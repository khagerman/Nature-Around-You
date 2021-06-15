BASE_URL = "https://api.inaturalist.org/v1";

$("#similar").on("click", async function (e) {
  e.preventDefault();
  $("#hidden_similar").show();
  getSimilarSpecies();
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
<div class="card" style="width: 10rem;">
    <img class="card-img-top" src="${photo}" style="width: 10rem;">
    <div class="card-body">
        <h6 class="card-text">${result.taxon.preferred_common_name}</h6>
      
    </div>
    <a href="${result.taxon.id}" class="stretched-link">
    </a>
</div>

`;
}

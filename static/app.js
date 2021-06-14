BASE_URL = "https://api.inaturalist.org/v1";

$("#simular").addEventListener("click", function (e) {
  e.preventDefault();
  getSimularSpecies();
});

async function getSimularSpecies() {
  const id = await axios.get("/simularspecies", {
    params: { nature_id: nature_id },
  });
  const res = await axios.get(
    `${BASE_URL}/identifications/similar_species?taxon_id=${id}`
  );
}

// function showCupcakes(cupcake) {
//   return `
// <div data-id=${cupcake.id} class="col">
// <li>Flavor:<b>${cupcake.flavor}</b>
// <ul>
//       <li>Size: ${cupcake.size}</li>
//       <li>${cupcake.rating}/5.0</li>
//     </ul>
// </li>
// <img class="img-thumbnail" width="100" height="110""
//             src="${cupcake.image}">

// `;
// }

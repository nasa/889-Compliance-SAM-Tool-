// ------------------------------------------------------------------------------
// Copyright 2022 by the U. S. Government as represented by the Administrator of 
// the National Aeronautics and Space Administration.  All Other Rights Reserved.
 
// The 889 Compliance SAM Tool is licensed under the Apache License, Version 2.0 
// (the "License"); you may not use this file except in compliance with the 
// License. You may obtain a copy of the License at 
// http://www.apache.org/licenses/LICENSE-2.0.
 
// Unless required by applicable law or agreed to in writing, software 
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT 
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the 
// License for the specific language governing permissions and limitations under 
// the License.
// ------------------------------------------------------------------------------

// capture some HTML elements as referencable objects
const resultsBox = document.getElementById('results-box');
const loadingBox = document.getElementById('loading-box');
const resultsList = document.getElementById('results-list');
const errorMessage = document.getElementById('error-message');
const form = document.getElementById('form');
const input = document.getElementById('input');
const showMore = document.getElementById('show-more');
const showMoreText = document.getElementById('show-more-text');
const showMoreIcon = document.getElementById('show-more-icon');
const noResults = document.getElementById('no-results');
const WARN_IF_FEWER_THAN_DAYS = 30;
const LOTS_OF_RESULTS = 40;
const DEFAULT_PAGE_SIZE = 10;

const getNonSelectableElement = function (
  legalBusinessName,
  eightEightNine,
  exclusions,
  dbaName,
  entityURL,
  city,
  stateOrProvinceCode,
  countryCode,
  ueiSAM,
  cageCode,
) {
  const resultsListItem = document.createElement('div');
  resultsListItem.className = 'disabled item';

  const downloadIcon = getDownloadIcon();
  downloadIcon.style = 'visibility:hidden';
  resultsListItem.appendChild(downloadIcon);

  const listItemContent = document.createElement('div');
  listItemContent.className = 'content';

  const listItemContentHeader = document.createElement('div');
  listItemContentHeader.className = 'ui small disabled header';
  listItemContentHeader.innerHTML = legalBusinessName;

  // It may be confusing to users if a non-selectable entity has mixed acceptable and non-acceptable labels.
  // Therefore, only show the reason the entity is non-selectable and hide check that passed.
  if (!eightEightNine.isCompliant) {
    const entityComplianceLabel = document.createElement('div');
    entityComplianceLabel.className = 'ui horizontal black label';
    entityComplianceLabel.innerHTML = eightEightNine.statusText;
    listItemContentHeader.appendChild(entityComplianceLabel);
  }
  if (exclusions.has_exclusions) {
    const entityComplianceLabel = document.createElement('div');
    entityComplianceLabel.className = 'ui horizontal black label';
    entityComplianceLabel.innerHTML = exclusions.statusText;
    listItemContentHeader.appendChild(entityComplianceLabel);
  }
  listItemContent.appendChild(listItemContentHeader);

  if (dbaName) {
    listItemContent.appendChild(getDbaNameElement(dbaName));
  }

  if (entityURL) {
    listItemContent.appendChild(getWebsiteElement(entityURL));
  }

  listItemContent.appendChild(
    getAddressAndCodesElement(city, stateOrProvinceCode, countryCode, ueiSAM, cageCode),
  );
  resultsListItem.appendChild(listItemContent);
  return resultsListItem;
};

const getSelectableElement = function (
  legalBusinessName,
  pdfLinks,
  eightEightNine,
  registrationExpirationDate,
  dbaName,
  entityURL,
  city,
  stateOrProvinceCode,
  countryCode,
  ueiSAM,
  cageCode,
) {
  const resultsListItem = document.createElement('a');
  resultsListItem.href = pdfLinks.entityPDF;
  resultsListItem.target = '_blank';
  resultsListItem.rel = 'noopener noreferrer';
  resultsListItem.className = 'item';

  resultsListItem.appendChild(getDownloadIcon());

  const resultsListItemContent = document.createElement('div');
  resultsListItemContent.className = 'content';

  resultsListItemContent.appendChild(
    getSelectableItemHeader(legalBusinessName, eightEightNine, registrationExpirationDate),
  );

  if (dbaName) {
    resultsListItemContent.appendChild(getDbaNameElement(dbaName));
  }

  if (entityURL) {
    resultsListItemContent.appendChild(getWebsiteElement(entityURL));
  }

  resultsListItemContent.appendChild(
    getAddressAndCodesElement(city, stateOrProvinceCode, countryCode, ueiSAM, cageCode),
  );
  resultsListItem.appendChild(resultsListItemContent);
  return resultsListItem;
};

const getSelectableItemHeader = function (
  legalBusinessName,
  eightEightNine,
  registrationExpirationDate,
) {
  const itemHeader = document.createElement('div');
  itemHeader.className = 'ui small header';
  itemHeader.innerHTML = legalBusinessName;

  itemHeader.appendChild(getSelectableComplianceLabel(eightEightNine));

  const registrationExpirationLabel = getRegistrationExpirationLabel(registrationExpirationDate);
  if (registrationExpirationLabel) {
    itemHeader.appendChild(registrationExpirationLabel);
  }
  return itemHeader;
};

const getSelectableComplianceLabel = function (eightEightNine) {
  const complianceLabel = document.createElement('div');
  complianceLabel.className = 'ui horizontal blue label';
  complianceLabel.innerHTML = eightEightNine.statusText;
  return complianceLabel;
};

const getRegistrationExpirationLabel = function (registrationExpirationDate) {
  const validTo = new Date(registrationExpirationDate);
  const today = new Date();
  const warningDaysFromNow = today.addDays(WARN_IF_FEWER_THAN_DAYS);
  if (validTo < warningDaysFromNow) {
    const year = new Intl.DateTimeFormat('en', { year: 'numeric' }).format(validTo);
    const month = new Intl.DateTimeFormat('en', { month: 'short' }).format(validTo);
    const day = new Intl.DateTimeFormat('en', { day: '2-digit' }).format(validTo);
    const entityValidToLabel = document.createElement('div');
    entityValidToLabel.className = 'ui horizontal orange label';
    entityValidToLabel.innerHTML = `Expiring registration: ${month}. ${day}, ${year}`;
    return entityValidToLabel;
  }
};

const getDownloadIcon = function () {
  const downloadIcon = document.createElement('i');
  downloadIcon.className = 'large file download middle aligned icon';
  return downloadIcon;
};

const getDbaNameElement = function (dbaName) {
  const element = document.createElement('div');
  element.className = 'description';
  element.style = 'padding-top: 0.2em;';
  element.innerHTML += '(' + dbaName + ')';
  return element;
};

const getWebsiteElement = function (URL) {
  const element = document.createElement('div');
  element.className = 'description';
  element.style = 'padding-top: 0.2em;';
  element.innerHTML += URL.replace(/^http:\/\//g, '')
    .replace(/^https:\/\//g, '')
    .replace(/\/$/g, '')
    .toLowerCase();
  return element;
};

const getAddressAndCodesElement = function (
  city,
  stateOrProvinceCode,
  countryCode,
  ueiSAM,
  cageCode,
) {
  const address = condensedAddress(city, stateOrProvinceCode, countryCode);
  const whitespace = '&nbsp;&nbsp;&nbsp;&nbsp;';
  const element = document.createElement('div');
  element.className = 'description';
  element.style = 'padding-top: 0.4em;';
  element.innerHTML = address;
  element.innerHTML += whitespace + 'SAM: ' + ueiSAM;
  if (cageCode != null) {
    element.innerHTML += whitespace + 'CAGE: ' + cageCode;
  }
  return element;
};

const condensedAddress = function (city, state, country) {
  let address = city + ',';
  if (state) {
    address += ' ' + state;
  }
  address += ' ' + country;
  return address;
};

Date.prototype.addDays = function (days) {
  var date = new Date(this.valueOf());
  date.setDate(date.getDate() + days);
  return date;
};

const renderResult = function (entity) {
  if (entity.samToolsData.isSelectable) {
    const resultsListItem = getSelectableElement(
      entity.entityRegistration.legalBusinessName,
      entity.samToolsData.pdfLinks,
      entity.samToolsData.eightEightNine,
      entity.entityRegistration.registrationExpirationDate,
      entity.entityRegistration.dbaName,
      entity.coreData.entityInformation.entityURL,
      entity.coreData.physicalAddress.city,
      entity.coreData.physicalAddress.stateOrProvinceCode,
      entity.coreData.physicalAddress.countryCode,
      entity.entityRegistration.ueiSAM,
      entity.entityRegistration.cageCode,
    );
    resultsList.appendChild(resultsListItem);
  } else {
    const resultsListItem = getNonSelectableElement(
      entity.entityRegistration.legalBusinessName,
      entity.samToolsData.eightEightNine,
      entity.samToolsData.exclusions,
      entity.entityRegistration.dbaName,
      entity.coreData.entityInformation.entityURL,
      entity.coreData.physicalAddress.city,
      entity.coreData.physicalAddress.stateOrProvinceCode,
      entity.coreData.physicalAddress.countryCode,
      entity.entityRegistration.ueiSAM,
      entity.entityRegistration.cageCode,
    );
    resultsList.appendChild(resultsListItem);
  }
};

const updateShowMore = function (response) {
  const currentResultsLength = resultsList.children.length;
  const numResultsLeft = response.totalRecords - currentResultsLength;
  const nextPageLength = Math.min(DEFAULT_PAGE_SIZE, numResultsLeft);
  const nextPageIndex = Math.floor(currentResultsLength / DEFAULT_PAGE_SIZE);

  showMore.style.display = 'block';
  if (currentResultsLength === 0) {
    showMore.style.display = 'none';
    resultsBox.style.display = 'none';
    showMoreIcon.style.display = 'none';
    noResults.style.display = 'inline-block';
  } else {
    if (numResultsLeft > 0) {
      noResults.style.display = 'none';
      showMoreIcon.style.display = 'inline-block';
      showMoreText.innerHTML =
        'Next ' + nextPageLength + ' results (' + numResultsLeft + ' remaining)';
      showMore.onclick = function (event) {
        getNextPage(nextPageIndex);
      };
    } else {
      showMoreIcon.style.display = 'none';
      showMoreText.innerHTML = '';
      showMore.style.display = 'none';
      showMore.onclick = function (event) {
        event.preventDefault();
      };
    }
  }
};

const searchXhttp = new XMLHttpRequest();
searchXhttp.onreadystatechange = function () {
  if (this.readyState === 4 && this.status === 200) {
    loadingBox.style.display = 'none';
    const response = JSON.parse(this.responseText);
    if (response.success) {
      noResults.style.display = 'none';
      for (const entity of response.entityData) {
        renderResult(entity);
      }
      updateShowMore(response);
    } else {
      noResults.style.display = 'none';
      resultsBox.style.display = 'none';
      errorMessage.style.display = 'inherit';
      errorMessage.innerHTML = response.errors[0];
    }
  } else if (this.readyState === 4 && this.status === 404) {
    noResults.style.display = 'none';
    resultsBox.style.display = 'none';
    errorMessage.style.display = 'inherit';
    errorMessage.innerHTML = this.statusText;
  }
};

const getNextPage = function (pageIndex) {
  loadingBox.style.display = 'inherit';
  // send the request with the request object
  const inputValue = input.value
    .replace(/http:\/\//g, '')
    .replace(/https:\/\//g, '')
    .replace(/[&|{}^\\:]/g, ' ');
  searchXhttp.open(
    'GET',
    '/api/entity-information/v3/entities?samToolsSearch=' +
      inputValue +
      '&includeSections=samToolsData,entityRegistration,coreData&registrationStatus=A&purposeOfRegistrationCode=Z2~Z5&entityEFTIndicator=&page=' +
      pageIndex,
    true,
  );
  searchXhttp.send();
};

// form onsubmit function (making a search request)
form.onsubmit = function (event) {
  event.preventDefault();
  resultsBox.style.display = 'inherit';

  resultsList.innerHTML = '';
  errorMessage.innerHTML = '';
  errorMessage.style.display = 'none';

  showMoreIcon.style.display = 'none';
  // showMore.className = 'ui segment';
  showMoreText.innerHTML = '';
  showMore.style.display = 'none';
  showMore.onclick = function (event) {
    event.preventDefault();
  };

  loadingBox.style.display = 'inherit';

  // send the request with the request object
  const inputValue = input.value
    .replace(/http:\/\//g, '')
    .replace(/https:\/\//g, '')
    .replace(/[&|{}^\\:]/g, ' ');
  searchXhttp.open(
    'GET',
    '/api/entity-information/v3/entities?samToolsSearch=' +
      inputValue +
      '&includeSections=samToolsData,entityRegistration,coreData&registrationStatus=A&purposeOfRegistrationCode=Z2~Z5&entityEFTIndicator=',
    true,
  );
  searchXhttp.send();
};
